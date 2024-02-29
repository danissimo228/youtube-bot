import time

from .const import BASE_URL_YOUTUBE, ProxyType, CountryCodeFlagEmoji, UPDATE_MESSAGE_BUTTONS
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from .models import Users, Proxy, Message, ProxySettings, session
from youtubesearchpython import VideosSearch, Channel
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import update, select, delete
from fake_useragent import UserAgent
from pycountry import countries
from aiogram import Bot
import multiprocessing
import requests
from .utils import (
    get_position_video,
    format_tag_response,
    get_seo_for_tags,
    format_video_stat_response,
    format_seo_response,
    format_channel_stat_response,
    template_tg_message, settings_data
)


useragent = UserAgent()


async def is_valid_url(url: str) -> bool:
    try:
        response = requests.get(url=url)
        return BASE_URL_YOUTUBE in url and response.status_code == 200
    except requests.exceptions.MissingSchema:
        return False


def get_emoji_by_country(country_name: str) -> str:
    country = countries.get(name=country_name)
    country_code = country.alpha_2 if country else None
    for code in CountryCodeFlagEmoji:
        if code.name == country_code:
            return code.value


def is_valid_proxy(proxy: Proxy) -> bool:
    proxy_dict = {
        "http": f"http://{proxy.host}",
        # "https": f"https://{host}"
    }
    try:
        response = requests.get("https://www.google.com", proxies=proxy_dict, timeout=5)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException as e:
        pass
        session.execute(
            update(Proxy)
            .where(Proxy.id == str(proxy.id))
            .values(is_valid=False)
        )
        session.commit()
        return False


def create_user(telegram_id: int, username: str, full_name: str) -> None:
    user = Users(telegram_id=telegram_id, username=username, full_name=full_name)
    session.add(user)
    session.commit()
    session.refresh(user)


def create_message(value: str, message_id: int, chat_id: int, user_id: int, video_id: str) -> None:
    user = get_user(telegram_id=user_id)
    message = Message(value=value, telegram_id=message_id, chat_id=chat_id, user_id=user.id, video_id=video_id)
    session.add(message)
    session.commit()
    session.refresh(message)


def get_message(message_id: int, user_id: int) -> Message:
    print(user_id)
    user = get_user(telegram_id=user_id)
    print(user)
    return session.execute(
        select(Message)
        .where(Message.telegram_id == message_id, Message.user_id == str(user.id))
    ).scalar()


def update_message(value: str, message_id: int) -> None:
    session.execute(
        update(Message)
        .where(Message.telegram_id == message_id)
        .values(value=value)
    )
    session.commit()


def get_user(telegram_id: int) -> Users | None:
    user = session.execute(
        select(Users)
        .where(Users.telegram_id == telegram_id)
    )
    return user.scalar()


def create_proxy(proxy_type_str: str, host: str, country_code: str, telegram_id: int) -> None:
    user = get_user(telegram_id=telegram_id)
    country = countries.get(alpha_2=country_code)
    if not country:
        raise Exception("Не верный код страны!")

    type_proxy = None
    for proxy_type in ProxyType:
        if proxy_type_str.lower() == proxy_type.value.lower():
            type_proxy = proxy_type.value

    if not type_proxy:
        raise Exception("Не верный тип прокси!")

    proxy = Proxy(type=type_proxy, host=host, country=country.name, user_id=user.id)
    session.add(proxy)
    session.commit()
    session.refresh(proxy)
    is_valid_proxy(proxy)


def delete_users_proxy(host: str) -> None:
    session.execute(
        delete(Proxy)
        .where(Proxy.host == host)
    )
    session.commit()


def get_users_proxies(telegram_id: int) -> list[Proxy]:
    user = get_user(telegram_id=telegram_id)
    proxies = session.execute(
            select(Proxy)
            .where(Proxy.user_id == str(user.id))
        )
    return proxies.scalars().all()


def get_valid_proxies() -> list[Proxy]:
    proxies = session.execute(
        select(Proxy)
        .where(Proxy.is_valid == True)
    )
    return proxies.scalars().all()


def create_proxy_settings(country: str, user_id: str) -> None:
    proxy_settings = ProxySettings(proxy_country=country, user_id=user_id)
    session.add(proxy_settings)
    session.commit()
    session.refresh(proxy_settings)


def get_proxy_settings(country: str, user_id: str) -> ProxySettings:
    proxy_settings = session.execute(
        select(ProxySettings)
        .where(ProxySettings.proxy_country == country, ProxySettings.user_id == user_id)
    )
    return proxy_settings.scalars().all()


def delete_proxy_settings(country: str, user_id: str) -> None:
    session.execute(
        delete(ProxySettings)
        .where(ProxySettings.proxy_country == country, ProxySettings.user_id == user_id)
    )
    session.commit()


def get_proxy_countries(user_id: str) -> tuple[InlineKeyboardMarkup, dict[str, str]] | None:
    keyboard_list = []
    keyboard_dict = {}
    valid_proxies = get_valid_proxies()
    proxy_countries = list(set([valid_proxy.country for valid_proxy in valid_proxies]))

    for proxy_country in proxy_countries:
        country_code = countries.get(name=proxy_country).alpha_2
        country_flag_emoji = [code.value for code in CountryCodeFlagEmoji if country_code == code.name]
        country_flag_emoji = country_flag_emoji[0] if country_flag_emoji else "Не определен."
        keyboard_text = f"{proxy_country} {country_flag_emoji}"
        if get_proxy_settings(country=proxy_country, user_id=user_id):
            keyboard_text += " ✅"
        keyboard_list.append(
            [InlineKeyboardButton(text=keyboard_text, callback_data=f"proxy_countries_{country_code}")]
        )
        keyboard_dict[keyboard_text] = f"proxy_countries_{country_code}"

    if not keyboard_list:
        return

    return InlineKeyboardBuilder(keyboard_list).as_markup(), keyboard_dict

import logging
from timeout_decorator import timeout


@timeout(45)
async def get_yt_statistics_data(
        user_id: str,
        video_id: str,
        msg_id: int,
        chat_id: int,
        bot: Bot
) -> dict[str, bool] | None:
    """Метод для получения всех данных по видео YouTube ID напрямую из YouTube"""
    data = {}
    # Забираем валидные прокси
    valid_proxies = []
    for proxy in get_valid_proxies():
        if get_proxy_settings(country=proxy.country, user_id=user_id):
            valid_proxies.append(proxy)

    await bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text='Получаем общие данные по видео...')
    time.sleep(1)

    # Получаем данные по видео из YouTube
    logging.info("10000000000000000909877")
    logging.info(video_id)
    try:
        video_data = VideosSearch.data(video_id=video_id)
    except TypeError as ex:
        print(ex)
        await bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text='Не валидный id видео.')
        return
    except Exception as ex:
        print(ex)
        await bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text='Не валидный статус код.')
        return

    data["video"] = video_data
    if valid_proxies:
        # Проверяем наличие ключевых слов у видео
        if video_data["keywords"]:
            task_data = []
            for connect in valid_proxies:
                if is_valid_proxy(connect):
                    for tag in video_data["keywords"]:
                        data_hz = {
                            "yt_id": video_id,
                            "tag": tag,
                            "connect": connect.__dict__
                        }
                        task_data.append(data_hz)
                else:
                    continue

            await bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text='Получаем данные по позиции тегов...')
            time.sleep(1)
            outputs = {}
            with multiprocessing.Pool(settings_data("count_process_check")) as pool:
                try:
                    outputs = pool.map(get_position_video, task_data)
                except Exception as ex:
                    logging.error(str(ex))

            # Форматируем данные по тегам
            tag_data = format_tag_response(outputs)
            await bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text='Анализируем данные по сео...')
            time.sleep(1)
            # seo = get_seo_for_tags(outputs, len(video_data["keywords"]))
            # seo_data = format_seo_response(seo)
            # Форматируем общую статистику по видео
            video_stat = format_video_stat_response(
                [
                    {"type": "view", "value": video_data["view"]},
                    {"type": "comment", "value": video_data["comment"]},
                    {"type": "like", "value": video_data["like"]},
                    {"type": "dislike", "value": video_data["dislike"]}
                ]
            )
            data["video"]["statistics"] = video_stat
            data["video"]["tags"] = tag_data
            # data["video"]["seo"] = seo_data
        else:
            # Вызываем ошибку если видео не найдено
            return {"video": False}
    else:
        # Вызываем ошибку если валидные прокси не найдены
        return {"proxy": False}

    # Переопределяем ключи и значения для video
    video_data["picture"] = video_data["thumbnails"][4]["url"]
    video_data["yt_id"] = video_data["id"]
    video_data["name"] = video_data["title"]
    video_data["channel"] = video_data["channel"]["id"]

    # Удаляем не нужные ключи из ключа video
    video_data_del_key_list = ["id", "title", "view", "comment", "like", "dislike", "thumbnails"]
    for k in video_data_del_key_list:
        video_data.pop(k)

    data["video"] = video_data

    # Получаем данные по каналу
    await bot.edit_message_text(message_id=msg_id, chat_id=chat_id, text='Получаем общие данные пок каналу...')
    time.sleep(1)
    channel_data = Channel.data(video_data["channel"])
    # Форматируем статистику общую по каналу
    channel_stat = format_channel_stat_response(
        [
            {"type": "subscriber", "value": channel_data["subscriber"]},
            {"type": "video", "value": channel_data["video"]},
            {"type": "view", "value": channel_data["view"]}
        ]
    )

    # Переопределяем ключи и значения для channel
    if channel_data.get("thumbnails", None):
        channel_data["picture"] = channel_data["thumbnails"][-1]["url"]
    channel_data["yt_id"] = channel_data["id"]
    channel_data["name"] = channel_data["title"]

    # Удаляем не нужные ключи из ключа channel
    channel_data_del_key_list = ["id", "title", "subscriber", "video", "view", "thumbnails"]
    for k in channel_data_del_key_list:
        channel_data.pop(k)

    data["channel"] = channel_data
    data["channel"]["statistics"] = channel_stat

    # Форматируем данные для сообщения в Telegram
    tg_message = template_tg_message(data)
    try:
        # Отправка сообщения в Telegram
        update_message(message_id=msg_id, value=tg_message)
        await bot.edit_message_text(
            message_id=msg_id, chat_id=chat_id, text=tg_message, reply_markup=UPDATE_MESSAGE_BUTTONS, parse_mode='HTML'
        )
        return
    except Exception as ex:
        # Вызываем ошибку если не удалось отправить сообщение в Telegram
        return {"result": False}
