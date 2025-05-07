from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


lang_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🇺🇿 O'zbekcha"),
        ],
        [
            KeyboardButton(text="🇷🇺 Русский"),
        ]
    ],
    resize_keyboard=True,
)

phone_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Telefon raqamini yuborish / Отправить номер телефона", request_contact=True),
        ]
    ],
    resize_keyboard=True,
)


phone_btn_uz = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Telefon raqamini yuborish", request_contact=True),
        ]
    ],
    resize_keyboard=True,
)

phone_btn_ru = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Отправить номер телефона", request_contact=True),
        ]
    ],
    resize_keyboard=True,
)