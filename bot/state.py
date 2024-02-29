from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    change_action = State()
    proxy = State()
    proxy_action = State()
    delete_proxy = State()
    add_proxy = State()
    input_youtube_url = State()
    get_youtube_statistics = State()
