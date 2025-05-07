from aiogram import types
from loader import dp
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

                if not shops:
                    await message.answer("Sizda hali hech qanday do‘kon mavjud emas.")
                    return

                # Aktiv do‘konlarni ajratib olish
                active_shops = [shop for shop in shops if shop.get("is_active")]

                if len(active_shops) == 1:
                    shop = active_shops[0]
                    await message.answer(
                        f"🟢 Aktiv do‘kon:\n\n"
                        f"📛 Nomi: {shop['shop_name']}\n"
                        f"📅 Tugash muddati: {shop['subscription_end']}"
                    )
                else:
                    text = "🛍 Sizning do‘konlaringiz:\n\n"
                    for i, shop in enumerate(shops, 1):
                        text += (
                            f"{i}) {shop['shop_name']}\n"
                            f"   ⏳ Tugash: {shop['subscription_end']}\n\n"
                        )
                    await message.answer(text)
            else:
                await message.answer("❌ Do‘konlar ro‘yxatini olishda xatolik yuz berdi.")
