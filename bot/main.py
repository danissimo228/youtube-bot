from aiogram import Bot, Dispatcher, Router, F
from multiprocessing import freeze_support
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from .state import Form
import logging
import asyncio
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove
)
from .service import (
    is_valid_url,
    create_user,
    create_proxy,
    get_user,
    get_users_proxies,
    get_emoji_by_country,
    delete_users_proxy,
    get_yt_statistics_data,
    create_message,
    get_message,
    get_proxy_countries,
    create_proxy_settings,
    delete_proxy_settings,
)
from .const import (
    CountryCodeFlagEmoji,
    BOT_TOKEN,
    ADMIN_IDS,
    ACTION_BUTTONS,
    PROXY_BUTTON_TEXT,
    SETTINGS_BUTTON_TEXT,
    PROXY_ACTION_BUTTONS,
    FOR_ADMIN_ACTION_BUTTONS,
    ADD_PROXY_ACTION_BUTTON_TEXT,
    DELETE_PROXY_ACTION_BUTTON_TEXT,
    GET_STATISTIC_OF_VIDEO_BUTTON_TEXT,
)


bot = Bot(BOT_TOKEN)
form_router = Router()


@form_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user = message.from_user
    markup = ACTION_BUTTONS
    if not get_user(telegram_id=user.id):
        create_user(telegram_id=user.id, username=user.username, full_name=user.full_name)
    if str(user.id) in ADMIN_IDS:
        markup = FOR_ADMIN_ACTION_BUTTONS
    await state.set_state(Form.change_action)
    await message.answer("Привет! Выбери действие.", reply_markup=markup)


@form_router.message(Form.change_action, F.text.lower() == SETTINGS_BUTTON_TEXT.lower())
async def settings(message: Message, state: FSMContext) -> None:
    user = get_user(telegram_id=message.from_user.id)
    result = get_proxy_countries(user_id=user.id)
    if not result:
        await message.answer("Нет доступных прокси.")
        return

    await message.answer("Настройки", reply_markup=result[0])


@form_router.callback_query(lambda callback_query: callback_query.data.startswith("proxy_countries_"))
async def update_settings(callback_query: CallbackQuery) -> None:
    user = get_user(telegram_id=callback_query.from_user.id)
    result = get_proxy_countries(user_id=user.id)
    if not result:
        await callback_query.message.answer("Прокси больше не доступно")
    buttons, dict_button = result
    country_code = callback_query.data.split("_")
    country_code = country_code[2] if len(country_code) > 2 else None
    from pycountry import countries
    country_name = [
        countries.get(alpha_2=code.name).name for code in CountryCodeFlagEmoji if code.name == country_code
    ][0]

    for key, value in dict_button.items():
        if country_name in key:
            if "✅" in key:
                delete_proxy_settings(country=country_name, user_id=user.id)
            else:
                create_proxy_settings(country=country_name, user_id=user.id)
            continue

    await bot.edit_message_text(
        text=callback_query.message.text,
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=get_proxy_countries(user_id=user.id)[0]
    )


@form_router.message(Form.change_action, F.text.lower() == PROXY_BUTTON_TEXT.lower())
async def proxy_action(message: Message, state: FSMContext) -> None:
    proxies_string = "Выберете действие:\n"
    proxies_dict = {}
    count = 0
    proxies = get_users_proxies(telegram_id=message.from_user.id)
    for proxy in proxies:
        count += 1
        emoji = "🟢" if proxy.is_valid else "🔴"
        flag = get_emoji_by_country(country_name=proxy.country)
        proxies_dict[str(count)] = proxy.host
        proxies_string += f"{emoji}{count}: {proxy.host} {flag}\n"
    await state.update_data(change_action=proxies_dict)
    await message.answer(proxies_string, reply_markup=PROXY_ACTION_BUTTONS)
    await state.set_state(Form.proxy_action)


@form_router.message(Form.proxy_action, F.text.lower() == DELETE_PROXY_ACTION_BUTTON_TEXT.lower())
async def change_number_proxy(message: Message, state: FSMContext) -> None:
    await message.answer("Выберете номер прокси", reply_markup=None)
    await state.set_state(Form.delete_proxy)


@form_router.message(Form.delete_proxy)
async def delete_proxy(message: Message, state: FSMContext) -> None:
    markup = ACTION_BUTTONS
    number = message.text
    if not number.isdigit():
        await message.answer("Не валидный номер прокси.")
        return

    if int(number) <= 0:
        await message.answer("Не валидный номер прокси.")
        return

    proxies = await state.get_data()
    proxy_host = proxies['change_action'].get(number, None)
    if not proxy_host:
        await message.answer("Не верный номер прокси")
        return
    delete_users_proxy(host=proxy_host)
    await state.set_state(Form.change_action)
    if str(message.from_user.id) in ADMIN_IDS:
        markup = FOR_ADMIN_ACTION_BUTTONS
    await message.answer("Удаление прошло успешно.", reply_markup=markup)


@form_router.message(Form.proxy_action, F.text.lower() == ADD_PROXY_ACTION_BUTTON_TEXT.lower())
async def send_proxy(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Пришли прокси в таком формате: country_code://type://login:password@ip:port",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Form.add_proxy)


@form_router.message(Form.add_proxy)
async def add_proxy(message: Message, state: FSMContext) -> None:
    markup = ACTION_BUTTONS
    proxy = message.text.split("://")
    telegram_id = message.from_user.id
    if not len(proxy) > 2:
        await message.answer("Не верный формат прокси.")
        return

    country_code, type_proxy, host = proxy[0], proxy[1], proxy[2]
    try:
        create_proxy(
            proxy_type_str=type_proxy, host=host, country_code=country_code, telegram_id=telegram_id
        )
        await state.set_state(Form.change_action)
        if str(telegram_id) in ADMIN_IDS:
            markup = FOR_ADMIN_ACTION_BUTTONS
        await message.answer("Прокси успешно добавлены.", reply_markup=markup)
    except Exception as ex:
        await message.answer(str(ex))


@form_router.message(Form.change_action, F.text.lower() == GET_STATISTIC_OF_VIDEO_BUTTON_TEXT.lower())
async def send_url(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.input_youtube_url)
    await message.answer("Пришлите ссылку на видео.", reply_markup=ReplyKeyboardRemove())


@form_router.message(Form.input_youtube_url)
async def get_url(message: Message, state: FSMContext) -> None:
    url = message.text
    if is_valid_url(url):
        await state.set_state(Form.get_youtube_statistics)
        msg = await message.answer("Ожидайте.")
        video_id = url.split("=")
        if len(video_id) > 1:
            user = get_user(telegram_id=message.from_user.id)
            create_message(
                value="Ожидайте.", message_id=msg.message_id, chat_id=msg.chat.id,
                user_id=message.from_user.id, video_id=video_id[1]
            )
            try:
                err = await get_yt_statistics_data(
                    user_id=user.id, video_id=video_id[1], msg_id=msg.message_id, chat_id=msg.chat.id, bot=bot
                )
            except TimeoutError:
                await bot.edit_message_text(
                    message_id=msg.message_id, chat_id=message.chat.id, text='Ошибка! Слишком долгое ожидание.'
                )
            logging.error("================================================================================")
            logging.error(err)
            if isinstance(err, dict):
                await bot.edit_message_text(
                    message_id=msg.message_id, chat_id=message.chat.id, text='Ошибка! Слишком долгое ожидание.'
                )
        else:
            await message.answer("Не валидный url.")
    else:
        await message.answer("Не валидный url.")


@form_router.callback_query(lambda callback_query: callback_query.data == "update_message")
async def update_message(callback_query: CallbackQuery) -> None:
    message = get_message(message_id=callback_query.message.message_id, user_id=callback_query.from_user.id)
    try:
        err = await get_yt_statistics_data(
            user_id=message.user_id, video_id=message.video_id, msg_id=message.telegram_id, chat_id=message.chat_id, bot=bot
        )
    except TimeoutError:
        await bot.edit_message_text(
            message_id=message.id, chat_id=message.chat_id, text='Ошибка! Слишком долгое ожидание.'
        )
    logging.error("================================================================================")
    logging.error(err)
    if isinstance(err, dict):
        await bot.edit_message_text(
            message_id=message.id, chat_id=message.chat_id, text='Ошибка! Попробуйте еще раз.'
        )


async def main() -> None:
    freeze_support()
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot, skip_updates=False)

if __name__ == '__main__':
    asyncio.run(main())

