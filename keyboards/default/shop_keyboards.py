from data.config import API_URL
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def get_shop_keyboard(shop_name_uz, shop_name_ru, shop_code, telegram_id, lang="uz"):
    base_url = "https://market-front.abruis.uz"
    shop_display = (
        f"🛍 {shop_name_uz}" if lang == "uz" and shop_name_uz else
        f"🛍 {shop_name_ru}" if lang == "ru" and shop_name_ru else
        "🛒 Barcha do'konlar" if lang == "uz" else
        "🛒 Все магазины"
    )
    if shop_code:
        web_url = f"{base_url}/?telegram_id={telegram_id}&shop_code={shop_code}"
    else:
        web_url = f"{base_url}/shop/?telegram_id={telegram_id}&shop_code={shop_code}"

    if lang == "ru":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(shop_display, web_app=WebAppInfo(url=web_url))],
                [
                    KeyboardButton(text="🛒 Мои заказы",
                                   web_app=WebAppInfo(
                                       url=f"{base_url}/orders/?telegram_id={telegram_id}&shop_code={shop_code}")),
                    KeyboardButton(text="️👤 Мой профиль",
                                   web_app=WebAppInfo(
                                       url=f"{base_url}/edit_profile/?telegram_id={telegram_id}&shop_code={shop_code}")),
                ],
                [KeyboardButton(text="⚙️ Настройки")]
            ],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(shop_display, web_app=WebAppInfo(url=web_url))],
                [
                    KeyboardButton(text="🛒 Buyurtmalarim",
                                   web_app=WebAppInfo(
                                       url=f"{base_url}/orders/?telegram_id={telegram_id}&shop_code={shop_code}")),
                    KeyboardButton(text="️👤 Profilim",
                                   web_app=WebAppInfo(
                                       url=f"{base_url}/edit_profile/?telegram_id={telegram_id}&shop_code={shop_code}"))
                ],
                [KeyboardButton(text="⚙️ Sozlamalar")]
            ],
            resize_keyboard=True
        )

    return keyboard


shop_keyboard_sozlamalar_ru = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌐 Изменить язык"),
            KeyboardButton(text="📨 Отзыв о магазине"),
        ],
        [
            KeyboardButton(text="🧑‍💼 Администратор магазина"),
            KeyboardButton(text="🤖 О боте")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ]

    ],
    resize_keyboard=True
)

shop_keyboard_sozlamalar_uz = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌐 Tilni o'zgartirish"),
            KeyboardButton(text="📨 Do'kon uchun izoh")
        ],
        [
            KeyboardButton(text="🧑‍💼 Do'kon Admin"),
            KeyboardButton(text="🤖 Bot haqida")
        ],
        [
            KeyboardButton(text="🔙 Orqaga")
        ]
    ],
    resize_keyboard=True
)

sozlama_lang_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="O'zbekcha 🇺🇿"),
            KeyboardButton(text="Русский 🇷🇺"),
        ]
    ],
    resize_keyboard=True,
)


def get_bot_keyboard_sozlamalar(telegram_id, shop_code, lang="uz"):
    base_url = "https://market-front.abruis.uz"
    web_url = f"{base_url}/shop/?telegram_id={telegram_id}&shop_code={shop_code}"
    # Tilga mos klaviatura
    if lang == "ru":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🤖 Администратор бота")
                ],
                [
                    KeyboardButton(text="🛍 Открыть магазин")
                ],
                [
                    KeyboardButton(text="🛒 Все магазины", web_app=WebAppInfo(url=web_url))
                ],
                [
                    KeyboardButton(text="⬅️ Назад")
                ]
            ],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🤖 Bot Admin")
                ],
                [
                    KeyboardButton(text="🛍 Do'kon yaratish")
                ],
                [
                    KeyboardButton(text="🛒 Barcha do'konlar", web_app=WebAppInfo(url=web_url))
                ],
                [
                    KeyboardButton(text="⬅️ Orqaga")
                ]
            ],
            resize_keyboard=True
        )
    return keyboard
