import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import API_URL
from loader import dp
from states.register import PaymentStates

import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def get_order_data(order_id: int, telegram_id):
    url = f"{API_URL}/product/order/detail/{order_id}/?telegram_id={telegram_id}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, ssl=ssl_context) as response:
                data = await response.json()
                # print(response.status, data)
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"❌ So‘rov xatosi: {response.status}")
                    return None
        except aiohttp.ClientError as e:
            print(f"❌ Aloqa xatosi: {e}")
            return None


@dp.callback_query_handler(lambda c: c.data.startswith("to'lov:"))
async def handle_payment(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    order_id = int(call.data.split(":")[1])
    await state.update_data(order_id=order_id)

    # API dan ma'lumotni olib tilni olamiz
    order_data = await get_order_data(order_id, call.from_user.id)
    lang = order_data["user"].get("language", "uz") if order_data else "uz"

    if lang == "ru":
        text = (
            "📌 <b>Выберите карту для оплаты:</b>\n\n"
            "💳 <b>Uzcard:</b> <code>8600 1234 5678 9012</code>\n👤 Isroilov Rustamjon\n\n"
            "💳 <b>Humo:</b> <code>8600 1234 5678 9012</code>\n👤 Isroilov Rustamjon\n\n"
            "💳 <b>Visa:</b> <code>9860 3456 7890 1234</code>\n👤 Isroilov Rustamjon\n\n"
            "💰 <b>Сумма оплаты:</b> <i>200 000 сум или 20$</i>\n\n"
            "📸 <b>После оплаты, пожалуйста, отправьте фото чека.</b>\n\n"
            "⚠️ <b>ВНИМАНИЕ!</b>\n"
            "❗️Если отправлен фейковый чек — пользователь <u>будет заблокирован</u>!\n"
        )
        button_text = "📤 Отправить чек"
    else:
        text = (
            "📌 <b>To‘lov uchun quyidagi kartalardan birini tanlang:</b>\n\n"
            "💳 <b>Uzcard:</b> <code>8600 1234 5678 9012</code>\n👤 Isroilov Rustamjon\n\n"
            "💳 <b>Humo:</b> <code>8600 1234 5678 9012</code>\n👤 Isroilov Rustamjon\n\n"
            "💳 <b>Visa:</b> <code>9860 3456 7890 1234</code>\n👤 Isroilov Rustamjon\n\n"
            "💰 <b>To‘lov miqdori:</b> <i>200 000 so‘m yoki 20$</i>\n\n"
            "📸 <b>Iltimos, to‘lovni amalga oshirgach, chek (kvitansiya) suratini yuboring.</b>\n\n"
            "⚠️ <b>ESLATMA!</b>\n"
            "❗️Yolg‘on chek yoki boshqa rasm yuborilsa — foydalanuvchi botdan <u>bloklanadi</u>!\n"
        )
        button_text = "📤 Chekni yuborish"

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=button_text, callback_data=f"chek_yuborish:{order_id}")
    )

    await call.message.answer(text, reply_markup=buttons, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("chek_yuborish:"))
async def handle_chek_button(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    order_id = int(call.data.split(":")[1])
    await state.update_data(order_id=order_id)
    await PaymentStates.waiting_for_chek.set()

    # API orqali user language
    order_data = await get_order_data(order_id, call.from_user.id)
    lang = order_data["user"].get("language", "uz") if order_data else "uz"

    if lang == "ru":
        msg = "📸 Пожалуйста, отправьте фото чека (не документом, а фото)."
    else:
        msg = "📸 Iltimos, to‘lovni amalga oshirgach, chek suratini yuboring (document emas)."

    await call.message.answer(msg)


@dp.message_handler(content_types=types.ContentType.PHOTO, state=PaymentStates.waiting_for_chek)
async def handle_photo_chek(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    data = await state.get_data()
    order_id = data.get("order_id")

    order_data = await get_order_data(order_id, telegram_id)
    if not order_data:
        await message.answer("❌ Buyurtma topilmadi.")
        return

    user = order_data['user']
    shop = user.get('active_shop')
    lang = user.get('language', 'uz')

    if not shop:
        await message.answer("❌ Do‘kon ma'lumotlari topilmadi.")
        return

    group_id = shop['group_id']

    caption = (
        f"📤 <b>{user['first_name']} {user['last_name']}</b> dan to‘lov cheki\n🧾 Buyurtma raqami: <code>#{order_id}</code>"
        if lang == "uz"
        else f"📤 <b>{user['first_name']} {user['last_name']}</b> отправил чек\n🧾 Номер заказа: <code>#{order_id}</code>"
    )

    await message.bot.send_photo(
        chat_id=group_id,
        photo=message.photo[-1].file_id,
        caption=caption,
        parse_mode="HTML"
    )

    success_msg = (
        "✅ Chekingiz qabul qilindi. Tez orada operatorlar siz bilan bog‘lanadi."
        if lang == "uz"
        else "✅ Ваш чек принят. Скоро оператор свяжется с вами."
    )

    await message.answer(success_msg)
    await state.finish()


@dp.message_handler(state=PaymentStates.waiting_for_chek)
async def handle_invalid_chek_input(message: types.Message):
    # oldindan order_id ni olish
    state_data = await message.get_current()
    state_data = await FSMContext.set_state(PaymentStates.waiting_for_chek)
    order_id = (await message.bot.current_state(user=message.from_user.id).get_data()).get("order_id")

    # order orqali til
    order_data = await get_order_data(order_id, message.from_user.id)
    lang = order_data["user"].get("language", "uz") if order_data else "uz"

    if lang == "ru":
        await message.answer(
            "❗ Пожалуйста, отправьте фотографию чека.\n\n"
            "📸 Чек — это подтверждение оплаты.\n\n"
            "Вы можете отправить повторно, если допустили ошибку."
        )
    else:
        await message.answer(
            "❗ Iltimos, to‘lov cheki fotosuratini yuboring.\n\n"
            "📸 Chek — bu to‘lov amalga oshirilganini ko‘rsatuvchi rasm.\n\n"
            "Agar xatolik bo‘lsa, yana yuborishingiz mumkin."
        )
