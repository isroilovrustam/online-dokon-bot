from aiogram import types
from loader import dp
from datetime import datetime
import aiohttp
from data.config import API_URL


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
