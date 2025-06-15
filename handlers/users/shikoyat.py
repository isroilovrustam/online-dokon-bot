import aiohttp
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import API_URL
# from data.config import GROUP_ID
from loader import dp, bot
from keyboards.inline.subscription_inline import ha_yoq_taklif_tasqid_ru, ha_yoq_taklif_tasqid_uz, ha_yoq_taklif_uz, \
    ha_yoq_taklif_ru
from states.profile_state import TaklifState
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


# from keyboards.default.shop_keyboards import


async def get_active_shop_group_id(user_id):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/botuser/{user_id}/", ssl=ssl_context) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    group_id = data.get("active_shop", {}).get("group_id")
                    return group_id
                else:
                    return None
        except Exception as e:
            return None


@dp.message_handler(text=["📨 Do'kon uchun izoh", "📨 Отзыв о магазине"])
async def enter_test(message: types.Message):
    if message.text == "📨 Do'kon uchun izoh":
        await message.answer(f"Salom {message.from_user.full_name}\nQanday taklifingiz bor ⁉️",
                             reply_markup=ha_yoq_taklif_uz)
    elif message.text == "📨 Отзыв о магазине":
        await message.answer(f"Здравствуйте, {message.from_user.full_name}\nКакое у вас предложение ⁉️",
                             reply_markup=ha_yoq_taklif_ru)


@dp.callback_query_handler(text='yoqtaklif_uz')
async def hsa(call: types.CallbackQuery):
    await call.message.answer("Taklif yuborish bekor qilindi!")
    await call.message.delete()


@dp.callback_query_handler(text='yoqtaklif_ru')
async def hsa(call: types.CallbackQuery):
    await call.message.answer("Отправка отзыва отменена!")
    await call.message.delete()


@dp.callback_query_handler(text='hataklif_uz')
async def hsa(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Marhamat taklifingizni yozishingiz mumkin!")
    await TaklifState.taklif.set()


@dp.callback_query_handler(text='hataklif_ru')
async def hsa(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Пожалуйста, напишите свой отзыв!")
    await TaklifState.taklif.set()


@dp.message_handler(state=TaklifState.taklif)
async def answer_fullname(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/botuser/{message.from_user.id}/", ssl=ssl_context) as response:
            if response.status == 200:
                data = await response.json()
                language = data.get("language", "uz")
    taklif = message.text

    await state.update_data(
        {"username": message.from_user.username}
    )

    await state.update_data(
        {"taklif": taklif}
    )

    # Ma`lumotlarni qayta o'qiymiz
    data = await state.get_data()
    taklif = data.get("taklif")
    if language == "ru":
        msg = f"{taklif}\n"

        await message.answer(msg, reply_markup=ha_yoq_taklif_tasqid_ru)
    elif language == "uz":
        msg = f"{taklif}\n"
        await message.answer(msg, reply_markup=ha_yoq_taklif_tasqid_uz)


@dp.callback_query_handler(state=TaklifState, text='hatakliftasdiq')
async def submit_data(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    username = data.get("username")
    taklif = data.get("taklif")

    msg = f"Taklif:\n\n"
    msg += f"👨‍💼 Username - {username}\n"
    msg += f"📝 Taklifingiz - {taklif}\n"

    user_id = call.from_user.id

    # ✅ async funksiya uchun `await` ishlatilmoqda
    group_id = await get_active_shop_group_id(user_id)

    if group_id is None:
        await call.message.answer("❌ Guruh ID aniqlanmadi. Admin bilan bog‘laning.")
        return

    try:
        await bot.send_message(group_id, msg)
        await call.message.answer("✅ Ma'lumotlaringiz yuborildi!")
    except Exception as e:
        await call.message.answer("🚫 Xabar yuborishda xatolik yuz berdi.")

    await call.message.delete()
    await state.finish()


@dp.callback_query_handler(state=TaklifState, text='yoqtakliftasdiq_uz')
async def hsa(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🚫 Ma'lumotingiz yuborilmadi!!!")
    await call.message.delete()
    await state.finish()


@dp.callback_query_handler(state=TaklifState, text='yoqtakliftasdiq_ru')
async def hsa(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("🚫 Ваша информация не была отправлена!")
    await call.message.delete()
    await state.finish()
