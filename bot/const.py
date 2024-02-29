from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
from enum import Enum
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = os.getenv("ADMIN_IDS").split(",")
BASE_URL_YOUTUBE = "https://www.youtube.com/watch?v="

DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_USER = os.getenv("DATABASE_USER")
DB_NAME = os.getenv("DATABASE_NAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


GET_STATISTIC_OF_VIDEO_BUTTON_TEXT = "Получить статистику видео."
PROXY_BUTTON_TEXT = "Прокси."
SETTINGS_BUTTON_TEXT = "Настройки"

FOR_ADMIN_ACTION_BUTTONS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=PROXY_BUTTON_TEXT),
            KeyboardButton(text=GET_STATISTIC_OF_VIDEO_BUTTON_TEXT)
        ],
        [
            KeyboardButton(text=SETTINGS_BUTTON_TEXT)
        ]
    ]
)
ACTION_BUTTONS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=GET_STATISTIC_OF_VIDEO_BUTTON_TEXT),
            KeyboardButton(text=SETTINGS_BUTTON_TEXT)
        ],
    ]
)


ADD_PROXY_ACTION_BUTTON_TEXT = "Добавить прокси."
DELETE_PROXY_ACTION_BUTTON_TEXT = "удалить прокси."

PROXY_ACTION_BUTTONS = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text=ADD_PROXY_ACTION_BUTTON_TEXT),
            KeyboardButton(text=DELETE_PROXY_ACTION_BUTTON_TEXT)
        ],
    ]

)

UPDATE_MESSAGE_BUTTONS = InlineKeyboardBuilder(
    [
        [InlineKeyboardButton(text="Обновить.", callback_data="update_message")],
    ]
).as_markup()


class ErrorMess(str, Enum):
    video_not_found = "Видео не найдены"
    valid_proxy_not_found = "Валидные прокси не найдены"
    proxy_invalid = "Прокси не валидный"
    tagdata_video_not_found = "Данные по видео не найдены"
    tags_not_found = "Теги не найдены"
    mess_success_send = "Сообщение успешно отправлено"
    mess_failed_send = "Ошибка при отправке сообщения"
    update_failed_tagdata = "Не удалось обновить запись"
    update_success_tagdata = "Запись успешно обновлена"


class ProxyType(str, Enum):
    """Типы прокси"""

    HTTP = "HTTP"
    HTTPS = "HTTPS"
    SOCKS4 = "SOCKS4"
    SOCKS5 = "SOCKS5"


class SettingsType(str, Enum):
    """Типы данных атрибутов настроек"""

    STR = "str"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    LIST = "list"
    TUPLE = "tuple"
    DICT = "dict"


class DynamicsType(str, Enum):
    """Типы динамки позиций"""

    UP = "Поднялось"
    DN = "Опустилось"
    NC = "Не изменилось"


class ConstData(str, Enum):
    YT_URL = "https://www.youtube.com"


class PositionDynamicsEmoji(str, Enum):
    UP = "⬆️"
    DN = "⬇️"
    NC = "⏺️"
    UN = "❓"


class CountryCodeFlagEmoji(str, Enum):
    AD = "🇦🇩"
    AE = "🇦🇪"
    AF = "🇦🇫"
    AG = "🇦🇬"
    AI = "🇦🇮"
    AL = "🇦🇱"
    AM = "🇦🇲"
    AO = "🇦🇴"
    AQ = "🇦🇶"
    AR = "🇦🇷"
    AS = "🇦🇸"
    AT = "🇦🇹"
    AU = "🇦🇺"
    AW = "🇦🇼"
    AX = "🇦🇽"
    AZ = "🇦🇿"
    BA = "🇧🇦"
    BB = "🇧🇧"
    BD = "🇧🇩"
    BE = "🇧🇪"
    BF = "🇧🇫"
    BG = "🇧🇬"
    BH = "🇧🇭"
    BI = "🇧🇮"
    BJ = "🇧🇯"
    BL = "🇧🇱"
    BM = "🇧🇲"
    BN = "🇧🇳"
    BO = "🇧🇴"
    BQ = "🇧🇶"
    BR = "🇧🇷"
    BS = "🇧🇸"
    BT = "🇧🇹"
    BV = "🇧🇻"
    BW = "🇧🇼"
    BY = "🇧🇾"
    BZ = "🇧🇿"
    CA = "🇨🇦"
    CC = "🇨🇨"
    CD = "🇨🇩"
    CF = "🇨🇫"
    CG = "🇨🇬"
    CH = "🇨🇭"
    CI = "🇨🇮"
    CK = "🇨🇰"
    CL = "🇨🇱"
    CM = "🇨🇲"
    CN = "🇨🇳"
    CO = "🇨🇴"
    CR = "🇨🇷"
    CU = "🇨🇺"
    CV = "🇨🇻"
    CW = "🇨🇼"
    CX = "🇨🇽"
    CY = "🇨🇾"
    CZ = "🇨🇿"
    DE = "🇩🇪"
    DJ = "🇩🇯"
    DK = "🇩🇰"
    DM = "🇩🇲"
    DO = "🇩🇴"
    DZ = "🇩🇿"
    EC = "🇪🇨"
    EE = "🇪🇪"
    EG = "🇪🇬"
    EH = "🇪🇭"
    ER = "🇪🇷"
    ES = "🇪🇸"
    ET = "🇪🇹"
    FI = "🇫🇮"
    FJ = "🇫🇯"
    FK = "🇫🇰"
    FM = "🇫🇲"
    FO = "🇫🇴"
    FR = "🇫🇷"
    GA = "🇬🇦"
    GB = "🇬🇧"
    GD = "🇬🇩"
    GE = "🇬🇪"
    GF = "🇬🇫"
    GG = "🇬🇬"
    GH = "🇬🇭"
    GI = "🇬🇮"
    GL = "🇬🇱"
    GM = "🇬🇲"
    GN = "🇬🇳"
    GP = "🇬🇵"
    GQ = "🇬🇶"
    GR = "🇬🇷"
    GS = "🇬🇸"
    GT = "🇬🇹"
    GU = "🇬🇺"
    GW = "🇬🇼"
    GY = "🇬🇾"
    HK = "🇭🇰"
    HM = "🇭🇲"
    HN = "🇭🇳"
    HR = "🇭🇷"
    HT = "🇭🇹"
    HU = "🇭🇺"
    ID = "🇮🇩"
    IE = "🇮🇪"
    IL = "🇮🇱"
    IM = "🇮🇲"
    IN = "🇮🇳"
    IO = "🇮🇴"
    IQ = "🇮🇶"
    IR = "🇮🇷"
    IS = "🇮🇸"
    IT = "🇮🇹"
    JE = "🇯🇪"
    JM = "🇯🇲"
    JO = "🇯🇴"
    JP = "🇯🇵"
    KE = "🇰🇪"
    KG = "🇰🇬"
    KH = "🇰🇭"
    KI = "🇰🇮"
    KM = "🇰🇲"
    KN = "🇰🇳"
    KP = "🇰🇵"
    KR = "🇰🇷"
    KW = "🇰🇼"
    KY = "🇰🇾"
    KZ = "🇰🇿"
    LA = "🇱🇦"
    LB = "🇱🇧"
    LC = "🇱🇨"
    LI = "🇱🇮"
    LK = "🇱🇰"
    LR = "🇱🇷"
    LS = "🇱🇸"
    LT = "🇱🇹"
    LU = "🇱🇺"
    LV = "🇱🇻"
    LY = "🇱🇾"
    MA = "🇲🇦"
    MC = "🇲🇨"
    MD = "🇲🇩"
    ME = "🇲🇪"
    MF = "🇲🇫"
    MG = "🇲🇬"
    MH = "🇲🇭"
    MK = "🇲🇰"
    ML = "🇲🇱"
    MM = "🇲🇲"
    MN = "🇲🇳"
    MO = "🇲🇴"
    MP = "🇲🇵"
    MQ = "🇲🇶"
    MR = "🇲🇷"
    MS = "🇲🇸"
    MT = "🇲🇹"
    MU = "🇲🇺"
    MV = "🇲🇻"
    MW = "🇲🇼"
    MX = "🇲🇽"
    MY = "🇲🇾"
    MZ = "🇲🇿"
    NA = "🇳🇦"
    NC = "🇳🇨"
    NE = "🇳🇪"
    NF = "🇳🇫"
    NG = "🇳🇬"
    NI = "🇳🇮"
    NL = "🇳🇱"
    NO = "🇳🇴"
    NP = "🇳🇵"
    NR = "🇳🇷"
    NU = "🇳🇺"
    NZ = "🇳🇿"
    OM = "🇴🇲"
    PA = "🇵🇦"
    PE = "🇵🇪"
    PF = "🇵🇫"
    PG = "🇵🇬"
    PH = "🇵🇭"
    PK = "🇵🇰"
    PL = "🇵🇱"
    PM = "🇵🇲"
    PN = "🇵🇳"
    PR = "🇵🇷"
    PS = "🇵🇸"
    PT = "🇵🇹"
    PW = "🇵🇼"
    PY = "🇵🇾"
    QA = "🇶🇦"
    RE = "🇷🇪"
    RO = "🇷🇴"
    RS = "🇷🇸"
    RU = "🇷🇺"
    RW = "🇷🇼"
    SA = "🇸🇦"
    SB = "🇸🇧"
    SC = "🇸🇨"
    SD = "🇸🇩"
    SE = "🇸🇪"
    SG = "🇸🇬"
    SH = "🇸🇭"
    SI = "🇸🇮"
    SJ = "🇸🇯"
    SK = "🇸🇰"
    SL = "🇸🇱"
    SM = "🇸🇲"
    SN = "🇸🇳"
    SO = "🇸🇴"
    SR = "🇸🇷"
    SS = "🇸🇸"
    ST = "🇸🇹"
    SV = "🇸🇻"
    SX = "🇸🇽"
    SY = "🇸🇾"
    SZ = "🇸🇿"
    TC = "🇹🇨"
    TD = "🇹🇩"
    TF = "🇹🇫"
    TG = "🇹🇬"
    TH = "🇹🇭"
    TJ = "🇹🇯"
    TK = "🇹🇰"
    TL = "🇹🇱"
    TM = "🇹🇲"
    TN = "🇹🇳"
    TO = "🇹🇴"
    TR = "🇹🇷"
    TT = "🇹🇹"
    TV = "🇹🇻"
    TW = "🇹🇼"
    TZ = "🇹🇿"
    UA = "🇺🇦"
    UG = "🇺🇬"
    UM = "🇺🇲"
    US = "🇺🇸"
    UY = "🇺🇾"
    UZ = "🇺🇿"
    VA = "🇻🇦"
    VC = "🇻🇨"
    VE = "🇻🇪"
    VG = "🇻🇬"
    VI = "🇻🇮"
    VN = "🇻🇳"
    VU = "🇻🇺"
    WF = "🇼🇫"
    WS = "🇼🇸"
    XK = "🇽🇰"
    YE = "🇾🇪"
    YT = "🇾🇹"
    ZA = "🇿🇦"
    ZM = "🇿🇲"
    UN = "🏳"
