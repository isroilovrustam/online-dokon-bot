from data.config import API_URL
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def get_shop_keyboard(shop_name, shop_code, telegram_id, lang="uz"):
    base_url = "https://market-front.abruis.uz"
    shop_display = f"🛍 {shop_name}" if shop_name else ("🛒 Barcha do'konlar" if lang == "uz" else "🛒 Все магазины")
    if shop_code:
        web_url = f"{base_url}/{shop_code}/?telegram_id={telegram_id}"
    else:
        web_url = f"{base_url}/shop/?telegram_id={telegram_id}"
    print(web_url)
    if lang == "ru":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(shop_display, web_app=WebAppInfo(url=web_url))],
                [
                    KeyboardButton(text="🛒 Мои заказы", web_app=WebAppInfo(url=web_url)),
                    KeyboardButton(text="☎️ Связь")
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
                    KeyboardButton(text="🛒 Buyurtmalarim", web_app=WebAppInfo(url=web_url)),
                    KeyboardButton(text="☎️ Bog'lanish", )
                ],
                [KeyboardButton(text="⚙️ Sozlamalar")]
            ],
            resize_keyboard=True
        )

    return keyboard


def get_shop_keyboard_sozlamalar(telegram_id, lang="uz"):
    base_url = "https://market-front.abruis.uz"
    web_url = f"{base_url}/shop/?telegram_id={telegram_id}"
    # Tilga mos klaviatura
    if lang == "ru":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🌐 Изменить язык"),
                    KeyboardButton(text="🛠 Техническая поддержка"),
                ],
                [
                    KeyboardButton(text="🛒 Все магазины", web_app=WebAppInfo(url=web_url))
                ],
                [
                    KeyboardButton(text="🔙 Назад")
                ]

            ],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🌐 Tilni o'zgartirish"),
                    KeyboardButton(text="🛠 Texnik yordam"),
                ],
                [
                    KeyboardButton(text="🛒 Barcha do'konlar",
                                   web_app=WebAppInfo(url=web_url))
                ],
                [
                    KeyboardButton(text="🔙 Orqaga")
                ]
            ],
            resize_keyboard=True
        )
    return keyboard


sozlama_lang_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="O'zbekcha 🇺🇿"),
            KeyboardButton(text="Русский 🇷🇺"),
        ]
    ],
    resize_keyboard=True,
)


