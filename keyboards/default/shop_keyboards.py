from data.config import API_URL
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

def get_shop_keyboard(shop_name=None, shop_code=None, lang="uz"):
    shop_display = f"{shop_name}" if shop_name else "✅ Aktiv do‘kon"
    web_url = f"{API_URL}/shop/detail/{shop_code}/" if shop_code else "https://terrapro.uz/"

    if lang == "ru":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(f"✅ Активный магазин", web_app=WebAppInfo(url=web_url))
                ],
                [
                    KeyboardButton("🛍 Список магазинов", web_app=WebAppInfo(url="https://terrapro.uz/"))
                ],
            ],
            resize_keyboard=True,
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(shop_display, web_app=WebAppInfo(url=web_url))
                ],
                [
                    KeyboardButton("🛍 Do‘konlar ro‘yxati", web_app=WebAppInfo(url="https://terrapro.uz/"))
                ],
            ],
            resize_keyboard=True,
        )

    return keyboard
