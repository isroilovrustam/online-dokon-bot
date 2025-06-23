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
    shop = order_data["user"]["active_shop"] if order_data else None

    if not shop:
        await call.message.answer("Do‘kon ma'lumotlari topilmadi.")
        return

    # Kartalar
    uz_card = shop.get("uz_card")
    uz_card_holder = shop.get("uz_card_holder")
    humo_card = shop.get("humo_card")
    humo_card_holder = shop.get("humo_card_holder")
    visa_card = shop.get("visa_card")
    visa_card_holder = shop.get("visa_card_holder")

    if lang == "ru":
        text = (
            f"🛒 <b>ЗАВЕРШИТЕ ПОКУПКУ</b> <code>#{order_id}</code>\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🏦 <b>ВЫБЕРИТЕ КАРТУ:</b>\n\n"
            f"💳 <i>UZCARD</i>\n"
            f"<code>{uz_card}</code>\n"
            f"👤 <b>{uz_card_holder}</b>\n\n"
            f"💳 <i>HUMO</i>\n"
            f"<code>{humo_card}</code>\n"
            f"👤 <b>{humo_card_holder}</b>\n\n"
            f"💎 <i>VISA</i>\n"
            f"<code>{visa_card}</code>\n"
            f"👤 <b>{visa_card_holder}</b>\n\n"
            "━━━━━━━━━━━━━━━━━\n"
            "📸 <b>СЛЕДУЮЩИЙ ШАГ:</b>\n"
            "После оплаты нажмите <b>📤 Отправить чек</b> и отправьте фото чека\n\n"
            "⚠️ <b>ВАЖНО:</b>\n"
            "❗️ Отправка поддельного чека приведёт к блокировке!"
        )

        button_text_1 = "📤 Отправить чек"
    else:
        # YANGI
        text = (
            f"🛒 <b>XARIDINGIZNI YAKUNLASH</b> <code>#{order_id}</code>\n"
            "━━━━━━━━━━━━━━━━━\n"
            "🏦 <b>KARTA TANLANG:</b>\n\n"
            f"💳 <i>UZCARD</i>\n"
            f"<code>{uz_card}</code>\n"
            f"👤 <b>{uz_card_holder}</b>\n\n"
            f"💳 <i>HUMO</i>\n"
            f"<code>{humo_card}</code>\n"
            f"👤 <b>{humo_card_holder}</b>\n\n"
            f"💎 <i>VISA</i>\n"
            f"<code>{visa_card}</code>\n"
            f"👤 <b>{visa_card_holder}</b>\n\n"
            "━━━━━━━━━━━━━━━━━\n"
            "📸 <b>KEYINGI QADAM:</b>\n"
            "To'lovni amalga oshirgach, <b>📤 Chekni yuborish</> bosib chek suratini yuboring\n\n"
            "⚠️ <b>MUHIM:</b>\n"
            "❗️ Soxta chek yuborish - bloklashga olib keladi!"
        )
        button_text_1 = "📤 Chekni yuborish"

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=button_text_1, callback_data=f"chek_yuborish:{order_id}"),
    )
    await call.message.answer(text, reply_markup=buttons, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("chek_yuborish:"))
async def handle_chek_button(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    order_id = int(call.data.split(":")[1])
    await state.update_data(order_id=order_id)

    order_data = await get_order_data(order_id, call.from_user.id)
    lang = order_data["user"].get("language", "uz") if order_data else "uz"

    if lang == "ru":
        msg = "📸 Пожалуйста, отправьте фото чека (не документом, а фото)."
        cancel_btn = "❌ Отменить"
    else:
        msg = "📸 Iltimos, to‘lovni amalga oshirgach, chek suratini yuboring (document emas)."
        cancel_btn = "❌ Bekor qilish"

    buttons = InlineKeyboardMarkup(row_width=1)
    buttons.row(InlineKeyboardButton(text=cancel_btn, callback_data="cancel_chek"))

    await call.message.answer(msg, reply_markup=buttons)
    await PaymentStates.waiting_for_chek.set()


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

    success_text_uz = (
        "🎉 <b>AJOYIB!</b>\n"
        "━━━━━━━━━━━━━━━━━\n"
        "✅ Chekingiz muvaffaqiyatli qabul qilindi\n"
        "⏰ <b>Keyingi qadamlar:</b>\n"
        "• 5-10 daqiqada admin tekshiradi\n"
        "• Tasdiqlangach sizga xabar beramiz\n"
    )
    success_text_ru = (
        "🎉 <b>ЗАМЕЧАТЕЛЬНО!</b>\n"
        "━━━━━━━━━━━━━━━━━\n"
        "✅ Ваш заказ успешно принят\n"
        "⏰ <b>Следующие шаги:</b>\n"
        "• Администратор проверит в течение 5-10 минут\n"
        "• Мы уведомим вас после подтверждения\n"
    )

    success_msg = (
        success_text_uz
        if lang == "uz"
        else success_text_ru
    )

    await message.answer(success_msg)
    await state.finish()


@dp.message_handler(state=PaymentStates.waiting_for_chek,
                    content_types=[types.ContentType.TEXT, types.ContentType.VIDEO, types.ContentType.AUDIO,
                                   types.ContentType.DOCUMENT])
async def handle_invalid_chek_input(message: types.Message, state: FSMContext):
    # FSM'dan order_id olish
    state_data = await state.get_data()
    order_id = state_data.get("order_id")

    # order orqali tilni aniqlash
    order_data = await get_order_data(order_id, message.from_user.id)
    lang = order_data["user"].get("language", "uz") if order_data else "uz"

    # Xabar yuborish
    if lang == "ru":
        text = (
            "❗ Пожалуйста, отправьте фотографию чека.\n\n"
            "📸 Чек — это подтверждение оплаты.\n\n"
            "Вы можете отправить повторно, если допустили ошибку."
        )
        cancel_btn = "❌ Отменить"
    else:
        text = (
            "❗ Iltimos, to‘lov cheki fotosuratini yuboring.\n\n"
            "📸 Chek — bu to‘lov amalga oshirilganini ko‘rsatuvchi rasm.\n\n"
            "Agar xatolik bo‘lsa, yana yuborishingiz mumkin."
        )
        cancel_btn = "❌ Bekor qilish"

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=cancel_btn, callback_data="cancel_chek")
    )
    await message.answer(text, reply_markup=buttons)


@dp.callback_query_handler(lambda c: c.data == "cancel_chek", state=PaymentStates.waiting_for_chek)
async def cancel_chek_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer()

    await call.message.edit_text("✅ Amal bekor qilindi. Bosh menyudan davom eting.")
