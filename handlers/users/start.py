import json
import re
import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.phone_button import phone_btn_ru, phone_btn_uz, lang_btn
from loader import dp
from data.config import API_URL
from states.register import RegisterState
from keyboards.default.shop_keyboards import get_shop_keyboard

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


@dp.message_handler(commands="start")
async def bot_start(message: types.Message, state: FSMContext):
    args = message.get_args()
    shop_code = args.replace("shop_", "")
    if args.startswith("shop_"):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/shop/by-code/{shop_code}/",
                                   ssl=ssl_context) as shop_resp:  # ssl=ssl_context,
                # print(shop_resp.json())
                if shop_resp.status == 400:
                    await message.answer("❌ Bu do‘kon botda aktiv emas.")
                    return

                elif shop_resp.status == 200:
                    # Foydalanuvchining aktiv do‘koni sifatida saqlab qo‘yamiz
                    await session.post(f"{API_URL}/botuser/set-active-shop/", ssl=ssl_context, json={
                        "telegram_id": str(message.from_user.id),
                        "shop_code": shop_code
                    })
                    # return

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context) as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    language = user_data.get("language", "uz")
                    shop_name_uz = None
                    shop_name_ru = None
                    shop_code = None
                    active_shop = user_data.get("active_shop")
                    # print(active_shop)
                    telegram_id = message.from_user.id

                    if active_shop:
                        is_active = active_shop.get("is_active")

                        # print(is_active)
                        if is_active:
                            shop_name_uz = active_shop.get("shop_name_uz")
                            shop_name_ru = active_shop.get("shop_name_ru")
                            shop_code = active_shop.get("shop_code")
                            keyboard = get_shop_keyboard(shop_name_uz=shop_name_uz, shop_name_ru=shop_name_ru,
                                                         shop_code=shop_code,
                                                         telegram_id=telegram_id, lang=language)
                        else:
                            keyboard = get_shop_keyboard(shop_name_uz=shop_name_uz, shop_name_ru=shop_name_ru,
                                                         shop_code=shop_code,
                                                         telegram_id=telegram_id, lang=language)
                    else:
                        keyboard = get_shop_keyboard(shop_name_uz=shop_name_uz, shop_name_ru=shop_name_ru,
                                                     shop_code=shop_code, telegram_id=telegram_id,
                                                     lang=language)
                    if language == "ru":
                        await message.answer(f"👋 Привет, {message.from_user.full_name}!\n\n", reply_markup=keyboard)
                    elif language == "uz":
                        await message.answer(f"👋 Salom, {message.from_user.full_name}!\n\n", reply_markup=keyboard)
                    await state.finish()
                except aiohttp.ContentTypeError:
                    await message.answer("⚠️ Xatolik yuz berdi: noto'g'ri formatdagi javob (JSON emas).")
                    await state.finish()
            else:
                await state.update_data(waiting_for_shop_code=shop_code)
                await message.answer(
                    "🌟 Xush kelibsiz! | Добро пожаловать!\n\n🇺🇿 O‘zbekcha  |  🇷🇺 Русский",
                    reply_markup=lang_btn)
                await RegisterState.waiting_for_language.set()


@dp.message_handler(state=RegisterState.waiting_for_language)
async def choose_language(message: types.Message, state: FSMContext):
    # Tilni tanlash va telefon raqamini yuborish
    lang = message.text
    if lang == "🇺🇿 O'zbekcha":
        await state.update_data(language="uz")
        await message.answer("📱 Telefon raqamingizni yuboring:",
                             reply_markup=phone_btn_uz)
    elif lang == "🇷🇺 Русский":
        await state.update_data(language="ru")
        await message.answer(
            "📱 Пожалуйста, отправьте ваш номер телефона:",
            reply_markup=phone_btn_ru)
    else:
        return
    await RegisterState.waiting_for_phone.set()


# Tasdiqlash kodi yuborish
@dp.message_handler(content_types=[types.ContentType.CONTACT, types.ContentType.TEXT],
                    state=RegisterState.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    user = message.from_user
    user_data = await state.get_data()
    language = user_data.get("language", "uz")  # Tilni olish
    shop_code = user_data.get("waiting_for_shop_code")
    if message.contact and message.contact.user_id == message.from_user.id:
        phone_number = message.contact.phone_number
    elif message.text and re.fullmatch(r'^\+998\d{9}$', message.text.strip()):
        phone_number = message.text.strip()
    else:

        await message.answer(
            "📵 Iltimos, +998 bilan boshlanadigan telefon raqamingizni yozing yoki tugmadan foydalaning." if language == "uz" else
            "📵 Пожалуйста, введите номер, начинающийся с +998, или нажмите на кнопку ниже."
        )
        return
    payload = {
        "phone_number": phone_number,
        "telegram_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "telegram_username": user.username,
        "language": language,
        "active_shop": shop_code,
    }
    # Backendga yuborish
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{API_URL}/botuser/register/", ssl=ssl_context,
                json=payload
        ) as resp:
            # print(resp.status)
            if resp.status != 201:
                error_text = await resp.text()
                # await message.answer(
                #     f"❌ Ro'yxatdan o'tishda xatolik yuz berdi: {resp.status}\n{error_text[:200]}"
                # )
                await state.finish()
                return

        # Ro'yxatdan o'tgandan so'ng foydalanuvchi ma'lumotlarini olish
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{user.id}/", ssl=ssl_context) as resp:
            if resp.status != 200:
                await message.answer(
                    "❌ Serverdan ma'lumot olishda xatolik yuz berdi." if language == "uz" else
                    "❌ Ошибка при получении данных с сервера."
                )
                await state.finish()
                return

            try:
                user_data = await resp.json()
            except json.decoder.JSONDecodeError as e:
                await message.answer(
                    "❌ Serverdan noto‘g‘ri ma'lumot keldi." if language == "uz" else
                    "❌ Сервер отправил неверные данные."
                )
                # print(f"JSON decode error: {e}")
                await state.finish()
                return

        # Shop ma'lumotlarini ajratib olish
    telegram_id = user.id
    language = user_data.get("language", "uz")
    active_shop = user_data.get("active_shop")
    shop_name_uz = shop_name_ru = shop_code = phone_number = None

    if active_shop and active_shop.get("is_active"):
        shop_name_uz = active_shop.get("shop_name_uz")
        shop_name_ru = active_shop.get("shop_name_ru")
        shop_code = active_shop.get("shop_code")

    # Klaviatura generatsiyasi
    keyboard = get_shop_keyboard(
        shop_name_uz=shop_name_uz,
        shop_name_ru=shop_name_ru,
        shop_code=shop_code,
        telegram_id=telegram_id,
        lang=language
    )

    # Xabar yuborish
    if language == "ru":
        await message.answer("✅ Ваш номер принят.", reply_markup=keyboard)
    else:
        await message.answer("✅ Telefon raqamingiz qabul qilindi.", reply_markup=keyboard)

    # Holatni tugatish
    await state.finish()
