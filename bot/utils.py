import datetime
import logging

import pycountry
from youtubesearchpython import *
from fake_useragent import UserAgent
from .const import ConstData, PositionDynamicsEmoji, CountryCodeFlagEmoji
from .models import Settings, session
from sqlalchemy import select
from pycountry import countries

useragent = UserAgent()


def format_video_stat_response(data: list) -> dict:
    """Функция для форматирования статистики видео"""

    update_date = datetime.datetime.today().strftime("%d.%m.%Y %H:%M")
    dynamic = None
    clear_data = {}
    for item in data:
        if "updated_at" in item:
            update_date = datetime.datetime.fromisoformat(item["updated_at"])
            update_date = update_date.strftime("%d.%m.%Y %H:%M")

        if "dynamic" in item:
            dynamic = item["dynamic"]

        data = {
            "type": item["type"],
            "value": item["value"],
            "dynamic": dynamic
        }
        if update_date not in clear_data:
            clear_data[update_date] = [data]
        else:
            if update_date in clear_data:
                clear_data[update_date].append(data)
            else:
                clear_data[update_date] = [data]

    return clear_data


def format_seo_response(data: list) -> dict:
    """Функция для форматирования СЕО"""

    update_date = datetime.datetime.today().strftime("%d.%m.%Y %H:%M")
    dynamic = ""
    clear_data = {}

    for item in data:
        value = item["value"]
        country = item["country"]

        if "updated_at" in item:
            update_date = datetime.datetime.fromisoformat(item["updated_at"])
            update_date = update_date.strftime("%d.%m.%Y %H:%M")

        if "dynamic" in item:
            dynamic = item["dynamic"]

        data = {
            "country": country,
            "value": value,
            "dynamic": dynamic
        }

        if update_date in clear_data:
            clear_data[update_date].append(data)
        else:
            clear_data[update_date] = [data]

    return clear_data


def get_position_video(data: dict) -> dict:
    """Функция получения позиции видео по тегу из YouTube"""

    country = countries.get(name=data["connect"]["country"])
    country_code = country.alpha_2

    # Формируем прокси подключение
    proxy = {
        "all://": f'{data["connect"]["type"].value}://{data["connect"]["host"]}'
    }
    search_depth_position = settings_data("search_depth_position")
    logging.error(search_depth_position)
    # Получаем позицию видео по тегу
    position = VideosSearch.position(video_id=data["yt_id"],
                                     query=data["tag"],
                                     region=country_code,
                                     limit=100,
                                     proxy=proxy,
                                     user_agent=useragent.random)

    # Добавляем новый ключ с позицией
    data["position"] = position
    data["country"] = data["connect"]["country"]

    return data


def format_channel_stat_response(data: list) -> dict:
    """Функция для форматирования статистики канала"""

    update_date = datetime.datetime.today().strftime("%d.%m.%Y %H:%M")
    dynamic = None
    clear_data = {}
    for item in data:
        if "updated_at" in item:
            update_date = datetime.datetime.fromisoformat(item["updated_at"])
            update_date = update_date.strftime("%d.%m.%Y %H:%M")

        if "dynamic" in item:
            dynamic = item["dynamic"]

        data = {
            "type": item["type"],
            "value": item["value"],
            "dynamic": dynamic
        }
        if update_date not in clear_data:
            clear_data[update_date] = [data]
        else:
            if update_date in clear_data:
                clear_data[update_date].append(data)
            else:
                clear_data[update_date] = [data]

    return clear_data


def settings_data(setting: str):
    setting = session.execute(
        select(Settings)
        .where(Settings.code == setting)
    )
    setting = setting.scalar()
    type_setting = setting.type
    value_setting = setting.value
    if type_setting == "str":
        return str(value_setting)
    elif type_setting == "bool":
        return bool(value_setting)
    elif type_setting == "int":
        return int(value_setting)
    elif type_setting == "float":
        return float(value_setting)
    elif type_setting == "list":
        return list(value_setting)
    elif type_setting == "tuple":
        return tuple(value_setting)
    elif type_setting == "dict":
        return dict(value_setting)


def format_tag_response(data: dict) -> dict:
    """Функция для форматирования тегов"""

    update_date = datetime.datetime.today().strftime("%d.%m.%Y %H:%M")
    dynamic = ""
    clear_data = {}

    for item in data:
        tag = item["tag"]
        position = item["position"]
        country = item["country"]

        if "updated_at" in item:
            update_date = datetime.datetime.fromisoformat(item["updated_at"])
            update_date = update_date.strftime("%d.%m.%Y %H:%M")

        if "dynamic" in item:
            dynamic = item["dynamic"]

        data = {
            "country": country,
            "position": position,
            "dynamic": dynamic
        }
        if tag not in clear_data:
            clear_data[tag] = {update_date: [data]}
        else:
            if update_date in clear_data[tag]:
                clear_data[tag][update_date].append(data)
            else:
                clear_data[tag][update_date] = [data]

    return clear_data


def get_seo_for_tags(data: list, tags_count) -> list:
    """Функция получения seo по позициям тегов"""

    seo = {}
    seo_data = []
    max_top_position = settings_data("max_top_position")

    # Определяем количество тегов которые находятся в топе исходя из настроек
    for item in data:
        if "id" in item:
            video_id = item["id"]
        else:
            video_id = ""
        proxy = item["connect"]["id"]
        if proxy in seo and item["position"] <= max_top_position:
            seo[proxy]["value"] += 1
        else:
            seo[proxy] = {"id": video_id, "connect": item["connect"], "country": item["connect"]["country"], "value": 0}

    # Определяем процент тегов находящихся в топе от их общего количества
    for key, value in seo.items():
        value["value"] = round((value["value"] * 100 / tags_count), 1)
        seo_data.append(value)

    return seo_data


def template_tg_message(data: dict) -> str:
    """Функция для форматирования сообщения в Telegram"""

    # Получаем данные по шаблону
    template_message = settings_data("template_tg_message")
    template_message = template_message.replace('\r', '')
    template_message = template_message.split('\n')

    channel_id = ""
    channel_name = ""
    channel_date_created = ""
    channel_country = ""
    # channel_language = ""
    channel_follower = ""
    channel_video = ""
    channel_view = ""
    video_id = ""
    video_name = ""
    video_upload_date = ""
    video_publish_date = ""
    video_duration = ""
    # video_language = ""
    video_category = ""
    video_like = ""
    video_dislike = ""
    video_comment = ""
    video_view = ""
    tags_data = ""
    seo_data = ""
    notification_users = ""

    if "notification_users" in template_message:
        # Получаем пользователей для уведомления
        notification_users = settings_data("notification_user_id")

    if (
            "channel_id" in template_message
            or "channel_name" in template_message
            or "channel_date_created" in template_message
            or "channel_country" in template_message
    ) and "channel" in data:
        channel_id = data["channel"]["yt_id"]

        # Преобразовываем дату создания канала в нужный формат
        channel_create = datetime.datetime.fromisoformat(str(data["channel"]["created"]))
        channel_create = channel_create.strftime("%d.%m.%Y %H:%M")

        # Получаем данные по стране канала
        try:
            country_channel_data = pycountry.countries.search_fuzzy(data["channel"]["country"])
            country_channel_flag = CountryCodeFlagEmoji[country_channel_data.alpha_2].value
        except Exception:
            country_channel_flag = CountryCodeFlagEmoji.UN.value

        # Формируем общие данные канала
        channel_id = f'🆔 <b>Channel ID</b>: <a href="{ConstData.YT_URL.value}/channel/{channel_id}">{channel_id}</a>\n'
        channel_name = f'📝 <b>Название</b>: {data["channel"]["name"]}\n'
        channel_date_created = f'🗓 <b>Дата создания</b>: {channel_create}\n'
        channel_country = f'{country_channel_flag} <b>Страна</b>: {data["channel"]["country"]}\n'
        # channel_language = f'{language_channel_flag} <b>Язык</b>: {language_channel_name}\n'
    if (
            "channel_follower" in template_message
            or "channel_video" in template_message
            or "channel_view" in template_message
    ) and "channel" in data and "statistics" in data["channel"]:
        channel_statistics = list(data["channel"]["statistics"].keys())[-1]

        # Формируем статистику канала
        for item in data["channel"]["statistics"][channel_statistics]:
            item_type = item["type"].upper()
            if item["value"]:
                value = '{0:,}'.format(int(item["value"])).replace(',', ' ')
            else:
                value = item["value"]
            try:
                dynamic = PositionDynamicsEmoji[item["dynamic"]].value
            except KeyError:
                dynamic = ""
            if "SUBSCRIBER" in item_type:
                channel_follower = f'👤 {dynamic} <b>Подписчики</b>: {value}\n'
            elif "VIDEO" in item_type:
                channel_video = f'🎥 {dynamic} <b>Всего видео</b>: {value}\n'
            elif "VIEW" in item_type:
                channel_view = f'👁‍🗨 {dynamic} <b>Всего просмотров</b>: {value}\n'

    if (
            "video_id" in template_message
            or "video_name" in template_message
            or "video_upload_date" in template_message
            or "video_publish_date" in template_message
            or "video_duration" in template_message
            or "video_category" in template_message
    ) and "video" in data:
        video_id = data["video"]["yt_id"]

        # Преобразовываем дату загрузки видео в нужный формат
        video_upload = datetime.datetime.fromisoformat(str(data["video"]["upload_date"]))
        video_upload = video_upload.strftime("%d.%m.%Y %H:%M")

        # Преобразовываем дату публикации видео в нужный формат
        video_publish = datetime.datetime.fromisoformat(str(data["video"]["publish_date"]))
        video_publish = video_publish.strftime("%d.%m.%Y %H:%M")

        # Формируем общие данные видео
        video_id = f'🆔 <b>YouTube ID</b>: <a href="{ConstData.YT_URL.value}/watch?v={video_id}">{video_id}</a>\n'
        video_name = f'📝 <b>Название</b>: {data["video"]["name"]}\n'
        video_upload_date = f'🗓 <b>Дата создания</b>: {video_upload}\n'
        video_publish_date = f'🗓 <b>Дата публикации</b>: {video_publish}\n'
        video_duration = f'🕑 <b>Продолжительность</b>: {data["video"]["duration"]}\n'
        video_category = f'🗂 <b>Категория</b>: {data["video"]["category"]}\n'
        # video_language = f'{language_video_flag} <b>Язык</b>: {language_video_name}\n'

    if (
            "video_like" in template_message
            or "video_dislike" in template_message
            or "video_comment" in template_message
            or "video_view" in template_message
    ) and "video" in data and "statistics" in data["video"]:
        video_statistics = list(data["video"]["statistics"].keys())[-1]

        # Формируем статистику видео
        for item in data["video"]["statistics"][video_statistics]:
            item_type = item["type"].upper()
            if item_type == "LIKE":
                continue
            if item["value"]:
                if "," in item["value"]:
                    value = '{0:,}'.format(int(item["value"].replace(",", ""))).replace(',', ' ')
                else:
                    value = '{0:,}'.format(int(item["value"])).replace(',', ' ')
            else:
                value = item["value"]
            try:
                dynamic = PositionDynamicsEmoji[item["dynamic"]].value
            except KeyError:
                dynamic = ""
            if "LIKE" in item_type:
                video_like = f'👍 {dynamic} <b>Лайки</b>: {value}\n'
            elif "DISLIKE" in item_type:
                video_dislike = f'👎 {dynamic} <b>Дизлайки</b>: {value}\n'
            elif "COMMENT" in item_type:
                video_comment = f'💬 {dynamic} <b>Комментарии</b>: {value}\n'
            elif "VIEW" in item_type:
                video_view = f'👁‍🗨 {dynamic} <b>Просмотров</b>: {value}\n'

    if "tags_data" in template_message and "video" in data and "tags" in data["video"]:
        # Формируем данные по тегам
        tags_data = []
        tags = data["video"]["tags"]
        for tag in tags:
            tag_date_list = []
            for date in tags[tag]:
                country_data_list = []
                for country in tags[tag][date]:

                    try:
                        country_flag = CountryCodeFlagEmoji[country["country"]].value
                    except KeyError:
                        country_flag = CountryCodeFlagEmoji.UN.value
                    try:
                        dynamic = PositionDynamicsEmoji[country["dynamic"]].value
                    except KeyError:
                        dynamic = ""
                    position = str(country["position"]).zfill(2)
                    if position == "99":
                        dynamic = "🛑"

                    country_data_item = f'{country_flag}{dynamic}:{position}'
                    country_data_list.append(country_data_item)

                countries_data = " | ".join(str(country_data) for country_data in country_data_list)
                tag_date_row = f'📅 <b>{date}</b>\n{countries_data}\n'
                tag_date_list.append(tag_date_row)

            tag_data_list = "".join(str(tag_date) for tag_date in tag_date_list)
            tag_data = (f'🏷 <b>Тег</b>: {tag}\n'
                        f'{tag_data_list}'
                        f'----------\n')
            tags_data.append(tag_data)

        tags_data = "".join(str(tag_data) for tag_data in tags_data)
        tags_data = tags_data + "\n"

    if "seo_data" in template_message and "video" in data and "seo" in data["video"]:
        seo = list(data["video"]["seo"].keys())[-1]
        # Формируем данные по СЕО
        seo_data_list = []
        for seo_item in data["video"]["seo"][seo]:
            try:
                country_flag = CountryCodeFlagEmoji[seo_item["country"]].value
            except KeyError:
                country_flag = CountryCodeFlagEmoji.UN.value
            try:
                dynamic = PositionDynamicsEmoji[seo_item["dynamic"]].value
            except KeyError:
                dynamic = ""
            seo_data_item = f'{country_flag}{dynamic}:{seo_item["value"]}'
            seo_data_list.append(seo_data_item)
        seo_data = " | ".join(str(seo_data) for seo_data in seo_data_list)
        seo_data = "🌐 <b>SEO</b>: " + seo_data + "\n"

    tg_message = (
            channel_id
            + channel_name
            + channel_date_created
            + channel_country
            # + channel_language
            + "----------\n"
            + channel_follower
            + channel_video
            + channel_view
            + "\n"
            + video_id
            + video_name
            + video_upload_date
            + video_publish_date
            + video_duration
            + video_category
            # + video_language
            + "----------\n"
            + video_like
            + video_dislike
            + video_comment
            + video_view
            + "\n"
            + seo_data
            + "\n"
            + tags_data
            + notification_users
    )

    return tg_message
