from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

check_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Obuna bo'lish", url='https://t.me/abruis_code')
        ],
        [
            InlineKeyboardButton(text="🔄 Obunani tekshirish", callback_data="check_subs")
        ]
    ]
)

ha_yoq = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("✅ Ha", callback_data='ha'),
            InlineKeyboardButton("🚫 Yoq", callback_data='yoq')
        ]
    ]
)

ha_yoq_taklif_uz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("✅ Ha", callback_data='hataklif_uz'),
            InlineKeyboardButton("🚫 Yoq", callback_data='yoqtaklif_uz')
        ]
    ]
)

ha_yoq_taklif_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("✅ Да", callback_data='hataklif_ru'),
            InlineKeyboardButton("🚫 Нет", callback_data='yoqtaklif_ru')
        ]
    ]
)

ha_yoq_taklif_tasqid_uz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("✅ Yuborish", callback_data='hatakliftasdiq'),
            InlineKeyboardButton("🚫 Bekor qilish", callback_data='yoqtakliftasdiq_uz')
        ]
    ]
)


ha_yoq_taklif_tasqid_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("✅ Отправить", callback_data='hatakliftasdiq'),
            InlineKeyboardButton("🚫 Отмена", callback_data='yoqtakliftasdiq_ru')
        ]
    ]
)
