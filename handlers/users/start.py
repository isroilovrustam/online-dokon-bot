import re
import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.phone_button import phone_btn_ru, phone_btn_uz, lang_btn
from keyboards.inline.sms_inline_button import sms_inline_btn_uz, sms_inline_btn_ru
from loader import dp
from data.config import API_URL
from states.register import RegisterState


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    # ✅ START ARGUMENT (shop_xxx) orqali do‘kon kodini olish
    args = message.get_args()
    if args.startswith("shop_"):
        shop_code = args.replace("shop_", "")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/shop/by-code/{shop_code}/") as shop_resp:
                if shop_resp.status == 200:
                    await session.post(f"{API_URL}/botuser/set-active-shop/", json={
                        "telegram_id": str(message.from_user.id),
                        "shop_code": shop_code
                    })
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/") as resp:
            if resp.status == 200:
                user_data = await resp.json()
                language = user_data.get("language", "uz")
                welcome_text = (
                    f"👋 Salom, {message.from_user.full_name}!\n\n"
                    if language == "uz" else
                    f"👋 Привет, {message.from_user.full_name}!\n\n"
                )
                await message.answer(welcome_text, parse_mode="Markdown")
                await state.finish()
            else:
                await message.answer("🌐 Iltimos, o'zingizga qulay tilni tanlang.\n\n🇺🇿 O'zbekcha yoki 🇷🇺 Русский",
                                     reply_markup=lang_btn)
                await RegisterState.waiting_for_language.set()


@dp.message_handler(state=RegisterState.waiting_for_language)
async def choose_language(message: types.Message, state: FSMContext):
    # Tilni tanlash va telefon raqamini yuborish
    lang = message.text
    if lang == "🇺🇿 O'zbekcha":
        await state.update_data(language="uz")
        await message.answer("📞 Telefon raqamingizni yuboring.\n\n👇 Tugmani bosing va raqamingizni ulashing:",
                             reply_markup=phone_btn_uz)
    elif lang == "🇷🇺 Русский":
        await state.update_data(language="ru")
        await message.answer(
            "📞 Пожалуйста, отправьте ваш номер телефона.\n\n👇 Нажмите на кнопку и поделитесь номером:",
            reply_markup=phone_btn_ru)
    else:
        return
    await message.delete()
    await RegisterState.waiting_for_phone.set()


# Tasdiqlash kodi yuborish
@dp.message_handler(content_types=[types.ContentType.CONTACT, types.ContentType.TEXT],
                    state=RegisterState.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    language = user_data.get("language", "uz")  # Tilni olish

    # Telefon raqamni aniqlash
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

    # Backendga yuborish
    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{API_URL}/botuser/register/",
                json={"phone_number": phone_number, "telegram_id": message.from_user.id}
        ) as resp:
            if resp.status == 201:
                await state.update_data(phone_number=phone_number)  # Telefon raqamini saqlash
                await message.answer(
                    "✅ Telefon raqamingiz qabul qilindi." if language == "uz" else "✅ Ваш номер принят.",
                    reply_markup=types.ReplyKeyboardRemove()
                )
                confirm_text = (
                    "📩 4 xonali tasdiqlash kodi olish uchun quyidagi \n<b>📲Kod olish</b> tugmasini bosing." if language == "uz"
                    else "📩 Чтобы получить 4-значный код, нажмите кнопку \n<b>📲Получить код</b> ниже."
                )
                await message.answer(confirm_text,
                                     reply_markup=sms_inline_btn_uz if language == "uz" else sms_inline_btn_ru)
                await RegisterState.waiting_for_code.set()
            else:
                await message.answer(
                    "❌ Telefon raqamini qabul qilib bo‘lmadi. Iltimos, qaytadan urinib ko‘ring." if language == "uz" else
                    "❌ Не удалось получить номер. Попробуйте снова."
                )


@dp.message_handler(lambda msg: msg.text.isdigit() and len(msg.text) == 4, state=RegisterState.waiting_for_code)
async def verify_code(message: types.Message, state: FSMContext):
    code = message.text
    user = message.from_user
    user_data = await state.get_data()
    phone_number = user_data.get("phone_number")
    language = user_data.get("language", "uz")

    if not phone_number:
        await message.answer(
            "⚠️ Iltimos, avval telefon raqamingizni yuboring." if language == "uz" else
            "⚠️ Пожалуйста, сначала отправьте номер телефона."
        )
        return

    payload = {
        "phone_number": phone_number,
        "code": code,
        "telegram_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "telegram_username": user.username,
        "language": language,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/botuser/verify_code/", json=payload) as resp:
            data = await resp.json()
            if resp.status == 200:
                await message.answer(
                    "🎉 Tabriklaymiz! Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz!" if language == "uz" else
                    "🎉 Поздравляем! Вы успешно зарегистрированы!"
                )
                await state.finish()
            elif resp.status == 400 and "expired" in data.get("detail", "").lower():
                await message.answer(
                    "⏳ Kod eskirgan. Yangi kod yuborildi, uni kiriting." if language == "uz" else
                    "⏳ Срок действия кода истек. Новый код отправлен, введите его."
                )
            else:
                await message.answer(
                    "❌ Kod noto‘g‘ri. Iltimos, qayta urinib ko‘ring." if language == "uz" else
                    "❌ Неверный код. Пожалуйста, попробуйте снова."
                )
