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
                    # print(user_data)
                    active_shop = user_data.get("active_shop")
                    if active_shop and active_shop.get("is_active"):
                        phone_number = active_shop.get("phone_number")
                        await message.answer(f"Bo‘lanish uchun: {phone_number}")
                    else:
                        await message.answer("Do‘kon aktiv emas.")
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
                    telegram_id = message.from_user.id
                    keyboard = get_bot_keyboard_sozlamalar(telegram_id=telegram_id, lang=language)
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
    text_1_uz="""
🛒 O‘z do‘koningizni ochmoqchimisiz?
Endi siz ham o‘zingizga tegishli Telegram onlayn do‘kon ochib, mahsulotlaringizni avtomatik tarzda xaridorlarga taqdim etishingiz mumkin!
Shunchaki quyidagi ma’lumotlarni yuboring — biz siz uchun hammasini tayyorlab beramiz:"""
    text_2_uz = """
📌 Do‘kon nomi
Siz ochmoqchi bo‘lgan do‘kon nomini yozing.
Masalan: "Zarina Fashion"

📞 Telefon raqami
Mijozlar sizga bog‘lana oladigan raqamni yuboring.
Masalan: +998 90 123 45 67

📝 Do‘kon haqida qisqacha ma’lumot
Do‘koningiz qanday mahsulotlar bilan shug‘ullanishini yozing.
Masalan: “Ayollar uchun liboslar va aksessuarlar”

🖼 Do‘kon logotipi (rasm)
Logotipingiz bo‘lsa, rasm sifatida yuboring.

📣 Telegram kanal linki (ixtiyoriy)
Mahsulotlar chiqadigan Telegram kanal manzilini yuboring.

👥 Telegram guruh ID si
Buyurtmalar tushadigan guruh ID sini yuboring.

📸 Instagram sahifasi linki (ixtiyoriy)
Masalan: https://www.instagram.com/abruis.uz/

🏬 Do‘kon turi
Do‘koningiz qaysi turga tegishli:

Faqat onlayn

Faqat oflayn

Har ikkisi

🗓 Abonement muddati
Nechi oylik aboniment olmoqchisiz.
"""

    text_1_ru = """
🛒 Хотите открыть свой магазин?
Теперь вы тоже можете открыть свой собственный онлайн-магазин в Telegram и автоматически предлагать свои товары покупателям!
Просто отправьте нам следующую информацию — и мы всё подготовим для вас:"""

    text_2_ru = """
📌 Название магазина  
Укажите название магазина, который вы хотите открыть.  
Например: "Zarina Fashion"

📞 Номер телефона  
Укажите номер, по которому с вами смогут связаться клиенты.  
Например: +998 90 123 45 67

📝 Краткое описание магазина  
Напишите, какими товарами занимается ваш магазин.  
Например: “Одежда и аксессуары для женщин”

🖼 Логотип магазина (изображение)  
Если у вас есть логотип, отправьте его в виде изображения.

📣 Ссылка на Telegram-канал (необязательно)  
Укажите ссылку на канал, где будут публиковаться товары.

👥 ID Telegram-группы  
Укажите ID группы, куда будут поступать заказы.


📸 Ссылка на Instagram-страницу (необязательно)  
Например: https://www.instagram.com/abruis.uz/

🏬 Тип магазина  
Укажите тип магазина:

Только онлайн  
Только офлайн  
И онлайн, и офлайн

🗓 Срок абонемента  
На сколько месяцев вы хотите приобрести абонемент.
"""
    if message.text == "🛍 Do'kon yaratish":
        await message.answer(text_1_uz)
        await message.answer(text_2_uz)

    elif message.text == "🛍 Открыть магазин":
        await message.answer(text_1_ru)
        await message.answer(text_2_ru)