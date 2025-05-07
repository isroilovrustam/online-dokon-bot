from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

sms_inline_btn_uz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📲 Kodni olish",
                url="https://t.me/abruis_sms_bot?start=unique_code"
            )
        ]
    ]
)

sms_inline_btn_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📲 Получить код",
                url="https://t.me/abruis_sms_bot?start=unique_code"
            )
        ]
    ]
)
