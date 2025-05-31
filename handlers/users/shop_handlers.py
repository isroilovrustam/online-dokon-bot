from aiogram import types
from loader import dp
from datetime import datetime
import aiohttp
from data.config import API_URL
import json

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


@dp.message_handler(commands="shop")
async def show_user_shops(message: types.Message):
    telegram_id = message.from_user.id

    params = {
        "telegram_id": telegram_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/shop/list/", params=params) as resp:
            if resp.status == 200:
                shops = await resp.json()
                # print(shops)
                if not shops:
                    await message.answer("Sizda hali hech qanday do‘kon mavjud emas.")
                    return
                else:
                    text_true = ''
                    text_false = ''

                    for shop in shops:
                        sub_end = datetime.fromisoformat(shop['subscription_end'])

                        formatted_date = sub_end.strftime('%d.%m.%Y %H:%M')

                        if shop['is_active'] == True:
                            text_true += (
                                f"{shop['shop_name']}\n"
                                f"⏳ Tugash: {formatted_date}\n\n"
                            )
                        else:
                            text_false += (
                                f"{shop['shop_name']}\n"
                                f"⚠️ Online Do'kon vaqtincha ishlamayabdi\n\n"
                            )
                    await message.answer(text_true + text_false)
            else:
                await message.answer("❌ Do‘konlar ro‘yxatini olishda xatolik yuz berdi.")


@dp.message_handler(text="☎️ Bog'lanish")
async def handle_contact_button(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    active_shop = user_data.get("active_shop")
                    if active_shop and active_shop.get("is_active"):
                        phone_number = active_shop.get("phone_number")
                        await message.answer(f"Bo‘lanish uchun: {phone_number}")
                    else:
                        await message.answer("Do‘kon aktiv emas.")
                except json.decoder.JSONDecodeError:
                    await message.answer("Xatolik yuz berdi.")
