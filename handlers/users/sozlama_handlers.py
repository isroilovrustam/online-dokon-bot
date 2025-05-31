import json

import aiohttp
from aiogram.types import ReplyKeyboardRemove

from data.config import API_URL
from loader import dp
from aiogram import types
from keyboards.default.shop_keyboards import get_shop_keyboard, sozlama_lang_btn, get_shop_keyboard_sozlamalar

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

@dp.message_handler(text=["⚙️ Sozlamalar", "⚙️ Настройки"])
async def get_sozlamalar(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    language = user_data.get("language", "uz")
                    telegram_id = message.from_user.id
                    keyboard = get_shop_keyboard_sozlamalar(telegram_id=telegram_id, lang=language)
                    if message.text == "⚙️ Sozlamalar":
                        await message.answer("Quydagilardan birini tanlang: ", reply_markup=keyboard)
                    elif message.text == "⚙️ Настройки":
                        await message.answer("Пожалуйста, выберите один из следующих пунктов:", reply_markup=keyboard)
                except aiohttp.ContentTypeError:
                    pass


@dp.message_handler(text=["🌐 Tilni o'zgartirish", "🌐 Изменить язык"])
async def get_tilni_ozgartirish(message: types.Message):
    await message.answer("O‘zbekcha 🇺🇿 | Русский 🇷🇺", reply_markup=sozlama_lang_btn)


@dp.message_handler(text=["O'zbekcha 🇺🇿", "Русский 🇷🇺"])
async def change_language(message: types.Message):
    user_id = message.from_user.id
    new_language = ''
    # Tanlangan tilni aniqlash
    if message.text == "O'zbekcha 🇺🇿":
        new_language = 'uz'
    elif message.text == "Русский 🇷🇺":
        new_language = 'ru'

    # Tilni yangilash
    async with aiohttp.ClientSession() as session:
        payload = {'language': new_language}
        async with session.patch(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context, json=payload) as response:
            if response.status != 200:
                await message.answer(
                    "Tilni o'zgartirishda xatolik yuz berdi ❌" if new_language == "uz" else "Ошибка при изменении языка ❌")
                return
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    # print(user_data)
                    language = user_data.get("language", "uz")
                    active_shop = user_data.get("active_shop")
                    # print(active_shop)

                    shop_name = None
                    shop_code = None

                    if active_shop and active_shop.get("is_active"):
                        shop_name = active_shop.get("shop_name")
                        shop_code = active_shop.get("shop_code")
                        telegram_id = user_id

                    keyboard = get_shop_keyboard(
                        shop_name=shop_name,
                        shop_code=shop_code,
                        telegram_id=telegram_id,
                        lang=language
                    )

                except json.decoder.JSONDecodeError:
                    keyboard = ReplyKeyboardRemove()  # fallback or empty

    text = (
        "✅ Sizning tilingiz o'zgartirildi: O'zbekcha 🇺🇿"
        if new_language == "uz"
        else "✅ Ваш язык был изменён на: Русский 🇷🇺"
    )
    await message.answer(text, reply_markup=keyboard)

@dp.message_handler(text=["🔙 Orqaga", "🔙 Назад"])
async def back_go(message: types.Message):
    telegram_id = message.from_user.id  # Always identified beforehand

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{telegram_id}/", ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    language = user_data.get("language", "uz")
                    active_shop = user_data.get("active_shop")

                    shop_name = None
                    shop_code = None

                    if active_shop and active_shop.get("is_active"):
                        shop_name = active_shop.get("shop_name")
                        shop_code = active_shop.get("shop_code")

                    keyboard = get_shop_keyboard(
                        shop_name=shop_name,
                        shop_code=shop_code,
                        telegram_id=telegram_id,
                        lang=language
                    )

                except json.decoder.JSONDecodeError:
                    keyboard = ReplyKeyboardRemove()  # Fallback for JSON decode error

            else:
                keyboard = ReplyKeyboardRemove()  # Fallback for non-200 HTTP status

    text = "Asosiy sahifa" if message.text == "🔙 Orqaga" else "Главная страница"
    await message.answer(text, reply_markup=keyboard)
