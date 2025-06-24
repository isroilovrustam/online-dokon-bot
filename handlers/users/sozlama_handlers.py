import json

import aiohttp
from aiogram.types import ReplyKeyboardRemove

from data.config import API_URL
from loader import dp
from aiogram import types
from keyboards.default.shop_keyboards import get_shop_keyboard, sozlama_lang_btn, shop_keyboard_sozlamalar_ru, \
    shop_keyboard_sozlamalar_uz

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def get_user_keyboard(telegram_id: int):
    """
    Telegram ID bo‘yicha foydalanuvchi tilini va faol do‘konini tekshirib,
    tegishli klaviaturani qaytaradi.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{telegram_id}/", ssl=ssl_context) as resp:
            if resp.status != 200:
                return ReplyKeyboardRemove(), "uz"

            try:
                user_data = await resp.json()
                language = user_data.get("language", "uz")
                active_shop = user_data.get("active_shop", {})

                if isinstance(active_shop, dict) and active_shop.get("is_active"):
                    keyboard = get_shop_keyboard(
                        shop_name_uz=active_shop.get("shop_name_uz"),
                        shop_name_ru=active_shop.get("shop_name_ru"),
                        shop_code=active_shop.get("shop_code"),
                        telegram_id=telegram_id,
                        lang=language
                    )
                    return keyboard, language
            except Exception:
                pass

    return ReplyKeyboardRemove(), "uz"


@dp.message_handler(text=["⚙️ Sozlamalar", "⚙️ Настройки"])
async def get_sozlamalar(message: types.Message):
    if message.text == "⚙️ Sozlamalar":
        await message.answer("Quydagilardan birini tanlang: ", reply_markup=shop_keyboard_sozlamalar_uz)
    elif message.text == "⚙️ Настройки":
        await message.answer("Пожалуйста, выберите один из следующих пунктов:",
                             reply_markup=shop_keyboard_sozlamalar_ru)


@dp.message_handler(text=["🌐 Tilni o'zgartirish", "🌐 Изменить язык"])
async def get_tilni_ozgartirish(message: types.Message):
    await message.answer("O‘zbekcha 🇺🇿 | Русский 🇷🇺", reply_markup=sozlama_lang_btn)


@dp.message_handler(text=["O'zbekcha 🇺🇿", "Русский 🇷🇺"])
async def change_language(message: types.Message):
    user_id = message.from_user.id
    new_language = 'uz' if message.text == "O'zbekcha 🇺🇿" else 'ru'

    async with aiohttp.ClientSession() as session:
        payload = {'language': new_language}
        async with session.patch(f"{API_URL}/botuser/{user_id}/", ssl=ssl_context, json=payload) as response:
            if response.status != 200:
                await message.answer(
                    "Tilni o'zgartirishda xatolik yuz berdi ❌" if new_language == "uz"
                    else "Ошибка при изменении языка ❌"
                )
                return

    keyboard, language = await get_user_keyboard(user_id)

    text = (
        "✅ Sizning tilingiz o'zgartirildi: O'zbekcha 🇺🇿"
        if new_language == "uz"
        else "✅ Ваш язык был изменён на: Русский 🇷🇺"
    )
    await message.answer(text, reply_markup=keyboard)


@dp.message_handler(text=["🔙 Orqaga", "🔙 Назад"])
async def back_go(message: types.Message):
    telegram_id = message.from_user.id
    keyboard, language = await get_user_keyboard(telegram_id)

    text = "Asosiy sahifa" if message.text == "🔙 Orqaga" else "Главная страница"
    await message.answer(text, reply_markup=keyboard)
