from aiogram import types
from aiogram.types import ReplyKeyboardRemove

from keyboards.default.shop_keyboards import get_shop_keyboard, get_bot_keyboard_sozlamalar, \
    shop_keyboard_sozlamalar_ru, shop_keyboard_sozlamalar_uz
from loader import dp
from datetime import datetime
import aiohttp
from data.config import API_URL
import json

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


@dp.message_handler(text=["🧑‍💼 Do'kon Admin", "🧑‍💼 Администратор магазина"])
async def handle_contact_button(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    active_shop = user_data.get("active_shop")
                    if message.text == "🧑‍💼 Do'kon Admin":
                        if active_shop and active_shop.get("is_active"):
                            phone_number = active_shop.get("phone_number")
                            shop_owner_username = active_shop.get("user")
                            await message.answer(
                                f"📞 <b>Do‘kon administratori bilan bog‘lanish</b>\n\n"
                                f"• Telefon raqami: <code>{phone_number}</code>\n"
                                f"• Telegram: @{shop_owner_username}"
                            )

                        else:
                            await message.answer("Do‘kon aktiv emas.")
                    elif message.text == "🧑‍💼 Администратор магазина":
                        if active_shop and active_shop.get("is_active"):
                            phone_number = active_shop.get("phone_number")
                            shop_owner_username = active_shop.get("user")
                            await message.answer(
                                f"📞 <b>Связаться с администратором магазина</b>\n\n"
                                f"• Телефон: <code>{phone_number}</code>\n"
                                f"• Telegram: @{shop_owner_username}"
                            )
                        else:
                            await message.answer("Магазин не активен.")
                except json.decoder.JSONDecodeError:
                    await message.answer("Xatolik yuz berdi.")


@dp.message_handler(text=["🤖 Bot haqida", "🤖 О боте"])
async def handle_bot_haqida(message: types.Message):
    text_uz = """
🛍 O‘z onlayn do‘koningizni oching — oson, tez va qulay!

Endi mahsulotlaringizni bevosita Telegram bot orqali sotishingiz mumkin!

📦 Har bir mahsulot haqida foydalanuvchilarga to‘liq ma’lumot taqdim etiladi.
🛒 Xaridorlar mahsulotni bot orqali tanlab, bir necha bosishda zakaz berishadi.
📲 Siz esa faqat buyurtmalarni qabul qilasiz — boshqa hammasi avtomatik!

💼 Agar siz ham shunday qulay onlayn do‘kon ochmoqchi bo‘lsangiz yoki abonement haqida batafsil ma’lumotni bilmoqchi bo‘lsangiz 👇
🤖 Bot admini bilan bog‘laning va o‘z brendingizni bugunoq boshlang!"""

    text_ru = """
🛍 Откройте свой онлайн-магазин — легко, быстро и удобно!

Теперь вы можете продавать свои товары напрямую через Telegram-бота!

📦 Каждому товару предоставляется полная информация для пользователей.
🛒 Покупатели выбирают товар через бота и оформляют заказ всего в несколько кликов.
📲 А вы просто принимаете заказы — всё остальное автоматизировано!

💼 Если вы тоже хотите открыть такой удобный онлайн-магазин или узнать подробнее об абонементе 👇
🤖 Свяжитесь с админом бота и начните свой бренд уже сегодня!"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    language = user_data.get("language", "uz")
                    shop_code = user_data.get("active_shop").get("shop_code")
                    telegram_id = message.from_user.id
                    keyboard = get_bot_keyboard_sozlamalar(telegram_id=telegram_id, shop_code=shop_code, lang=language)
                    if message.text == "🤖 Bot haqida":
                        await message.answer(text_uz, reply_markup=keyboard)
                    elif message.text == "🤖 О боте":
                        await message.answer(text_ru, reply_markup=keyboard)
                except json.decoder.JSONDecodeError:
                    await message.answer("Xatolik yuz berdi.")


@dp.message_handler(text=["⬅️ Orqaga", "⬅️ Назад"])
async def back_go(message: types.Message):
    if message.text == "⬅️ Orqaga":
        await message.answer("⚙️ Sozlamalar bo'limi: ", reply_markup=shop_keyboard_sozlamalar_uz)
    elif message.text == "⬅️ Назад":
        await message.answer("⚙️ Раздел настроек: ", reply_markup=shop_keyboard_sozlamalar_ru)


@dp.message_handler(text=["🛍 Do'kon yaratish", "🛍 Открыть магазин"])
async def bot_admin(message: types.Message):
    text_1_uz = """
🛒 O‘z do‘koningizni ochmoqchimisiz?
Endi siz ham Telegram’da o‘zingizga tegishli onlayn do‘kon ochib, mahsulotlaringizni avtomatik tarzda xaridorlarga taqdim etishingiz mumkin!
Shunchaki quyidagi ma’lumotlarni yuboring — biz hammasini siz uchun tayyorlab beramiz:
"""

    text_2_uz = """
📌 Do‘kon nomi  
Ochmoqchi bo‘lgan do‘kon nomini yozing.  
Masalan: "Zarina Fashion"

📞 Telefon raqami  
Mijozlar sizga bog‘lana oladigan telefon raqamingizni yuboring.  
Masalan: +998 90 123 45 67

📝 Do‘kon haqida qisqacha ma’lumot  
Do‘koningiz qanday mahsulotlar bilan shug‘ullanishini yozing.  
Masalan: “Ayollar uchun liboslar va aksessuarlar”

🖼 Do‘kon logotipi (rasm)  
Agar logotipingiz bo‘lsa, uni rasm sifatida yuboring.

📣 Telegram kanal havolasi (ixtiyoriy)  
Mahsulotlar joylanadigan Telegram kanal manzilini yuboring.

👥 Telegram guruh ID raqami  
Buyurtmalar yuboriladigan guruhning ID raqamini yuboring.

📸 Instagram sahifasi havolasi (ixtiyoriy)  
Masalan: https://www.instagram.com/abruis.uz/

🏬 Do‘kon turi  
Do‘koningiz qaysi turga mansub ekanligini tanlang:  
• Faqat onlayn  
• Faqat oflayn  
• Har ikkisi

🗓 Abonement muddati  
Necha oylik obuna (abonement) olmoqchisiz? Belgilang.
"""

    text_1_ru = """
🛒 Хотите открыть свой магазин?
Теперь вы тоже можете открыть собственный онлайн-магазин в Telegram и автоматически предлагать свои товары покупателям!
Просто отправьте нам следующую информацию — и мы всё подготовим для вас:
"""

    text_2_ru = """
📌 Название магазина  
Укажите название магазина, который вы хотите открыть.  
Например: "Zarina Fashion"

📞 Номер телефона  
Укажите номер, по которому клиенты смогут с вами связаться.  
Например: +998 90 123 45 67

📝 Краткое описание магазина  
Напишите, какими товарами занимается ваш магазин.  
Например: “Одежда и аксессуары для женщин”

🖼 Логотип магазина (изображение)  
Если у вас есть логотип, отправьте его как изображение.

📣 Ссылка на Telegram-канал (необязательно)  
Укажите ссылку на канал, где будут публиковаться товары.

👥 ID Telegram-группы  
Укажите ID группы, куда будут поступать заказы.

📸 Ссылка на Instagram-страницу (необязательно)  
Например: https://www.instagram.com/abruis.uz/

🏬 Тип магазина  
Укажите тип магазина:  
• Только онлайн  
• Только офлайн  
• Онлайн и офлайн

🗓 Срок абонемента  
На сколько месяцев вы хотите приобрести абонемент?
"""

    if message.text == "🛍 Do'kon yaratish":
        await message.answer(text_1_uz)
        await message.answer(text_2_uz)

    elif message.text == "🛍 Открыть магазин":
        await message.answer(text_1_ru)
        await message.answer(text_2_ru)


@dp.message_handler(text=["🤖 Bot Admin", "🤖 Администратор бота"])
async def back_go(message: types.Message):
    text_uz = """
🛠 Botda biron muammo yuzaga kelsa, biz bilan bog‘laning:

📞 Telefon: +998 90 059 96 26  
📨 Telegram: @isroilov_rustam

⏱ Qisqa vaqt ichida sizga javob beramiz!
    """
    text_ru = """
🛠 Если у вас возникли проблемы с ботом, свяжитесь с нами:

📞 Телефон: +998 90 059 96 26  
📨 Телеграм: @isroilov_rustam

⏱ Мы ответим вам в кратчайшие сроки!

    """
    if message.text == "🤖 Bot Admin":
        await message.answer(text_uz)
    elif message.text == "🤖 Администратор бота":
        await message.answer(text_ru)
