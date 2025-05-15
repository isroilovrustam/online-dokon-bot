import re
import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.phone_button import phone_btn_ru, phone_btn_uz, lang_btn
from loader import dp
from data.config import API_URL
from states.register import RegisterState
# from keyboards.default.shop_keyboards import uzb_shop_btn, rus_shop_btn
from keyboards.default.shop_keyboards import get_shop_keyboard
# import ssl
#
# ssl_context = ssl.create_default_context()
# ssl_context.check_hostname = False
# ssl_context.verify_mode = ssl.CERT_NONE


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    args = message.get_args()
    if args.startswith("shop_"):
        shop_code = args.replace("shop_", "")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/shop/by-code/{shop_code}/") as shop_resp:
                if shop_resp.status == 400:
                    await message.answer("❌ Do'kon botda aktiv emas")
                if shop_resp.status == 200:
                    await session.post(f"{API_URL}/botuser/set-active-shop/", json={
                        "telegram_id": str(message.from_user.id),
                        "shop_code": shop_code
                    })
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/") as resp:
            if resp.status == 200:
                try:
                    user_data = await resp.json()
                    language = user_data.get("language", "uz")
                    # Do‘kon nomini olish (agar mavjud bo‘lsa)
                    shop_name = None
                    if user_data.get("active_shop"):
                        # active_shop obyekt yoki string bo'lishi mumkin, tekshiramiz:
                        if isinstance(user_data["active_shop"], dict):
                            shop_name = user_data["active_shop"].get("shop_name")
                        elif isinstance(user_data["active_shop"], str):
                            # faqat kod bo‘lishi mumkin, nom yo‘q
                            shop_name = user_data["active_shop"]
                        # Tugma yasash
                        keyboard = get_shop_keyboard(shop_name=shop_name, lang=language)
                    if language == "ru":
                        await message.answer(f"👋 Привет, {message.from_user.full_name}!\n\n", reply_markup=keyboard)
                    elif language == "uz":
                        await message.answer(f"👋 Salom, {message.from_user.full_name}!\n\n", reply_markup=keyboard)
                    await state.finish()
                except aiohttp.ContentTypeError:
                    await message.answer("⚠️ Xatolik yuz berdi: noto'g'ri formatdagi javob (JSON emas).")
                    await state.finish()
            else:
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
    }

    # Backendga yuborish
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{API_URL}/botuser/register/",
                json=payload
        ) as resp:
            # Do‘kon nomini olish (agar mavjud bo‘lsa)
            shop_name = None
            if user_data.get("active_shop"):
                # active_shop obyekt yoki string bo'lishi mumkin, tekshiramiz:
                if isinstance(user_data["active_shop"], dict):
                    shop_name = user_data["active_shop"].get("shop_name")
                elif isinstance(user_data["active_shop"], str):
                    # faqat kod bo‘lishi mumkin, nom yo‘q
                    shop_name = user_data["active_shop"]
                # Tugma yasash
                keyboard = get_shop_keyboard(shop_name=shop_name, lang=language)
            if resp.status == 201:
                await state.update_data(phone_number=phone_number)  # Telefon raqamini saqlash
                if language == "ru":
                    await message.answer("✅ Ваш номер принят.", reply_markup=keyboard)
                elif language == "uz":
                    await message.answer("✅ Telefon raqamingiz qabul qilindi.", reply_markup=keyboard)
                await state.finish()
            else:
                await message.answer(
                    "❌ Telefon raqamini qabul qilib bo‘lmadi. Iltimos, qaytadan urinib ko‘ring." if language == "uz" else
                    "❌ Не удалось получить номер. Попробуйте снова."
                )
