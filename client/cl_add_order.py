from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_create import bot, admins
from keyboards import inkb_client_menu
from keyboards import inkb_order_cancel
from sql import client_requests, menu_requests
import re


class FSMorder(StatesGroup):
    order_data = State()
    order_email = State()
    order_phone = State()
    order_address = State()
    order_memory = State()


async def client_order_start(callback: types.CallbackQuery):
    article = callback.data.split("_")[1]
    order_value = callback.data.split("_")[2]
    data_sql = await menu_requests.sql_find_article_warehouse(article)
    inkb = InlineKeyboardMarkup()
    user_data = await client_requests.sql_search_client(callback.from_user.id)
    if user_data:
        for i in data_sql:
            if i[3] >= 1:
                inkb.add(InlineKeyboardButton(text=i[2], callback_data=f'mord_{article}_{i[2]}_{order_value}'))
        await callback.message.answer(
            f'Список доступных размеров ниже.\nПожалуйста, выберите размер?',
            reply_markup=inkb.add(InlineKeyboardButton(text="Меню", callback_data='start')),
            disable_notification=True)
    else:
        for i in data_sql:
            if i[3] >= 1:
                inkb.add(InlineKeyboardButton(text=i[2], callback_data=f'{article}_{i[2]}_{order_value}'))
        await FSMorder.order_data.set()
        await callback.message.answer(
            f'Список доступных размеров ниже.\nПожалуйста, выберите размер?',
            reply_markup=inkb.add(InlineKeyboardButton(text="Меню", callback_data='start')),
            disable_notification=True)
    await callback.answer()


async def client_order_step1(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['order_data'] = callback.data
    await FSMorder.next()
    await callback.message.answer(
        f'Пожалуйста, укажите Ваш адрес электронной почты?', reply_markup=inkb_order_cancel, disable_notification=True)
    await callback.answer()


async def client_order_step2(message: types.Message, state: FSMContext):
    regex = re.compile(
        r"(?![.+\-])[A-z\d'._+-]{1,64}(?<![.+\-])@(?![.+\-])[A-z\d'._+-]{1,251}\.[A-z]{1,4}(?<![.+\-])")
    if re.fullmatch(regex, message.text):
        async with state.proxy() as data:
            data['order_email'] = message.text
        await FSMorder.next()
        await message.answer(
            f'Пожалуйста, укажите Ваш мобильный номер телефона через 8?\n<i>(Например, 89876543210)</i>',
            reply_markup=inkb_order_cancel, disable_notification=True)
    else:
        await message.answer(
            f'Ошибка, адрес электронной почты указан не правильно!', reply_markup=inkb_order_cancel,
            disable_notification=True)


async def client_order_step3(message: types.Message, state: FSMContext):
    regex = re.compile(r"(?!\+)[7,8]9\d{9}")
    if re.fullmatch(regex, message.text):
        async with state.proxy() as data:
            data['order_phone'] = message.text
        await FSMorder.next()
        await message.answer(
            f'Пожалуйста, укажите Ваш адрес полностью?\n<i>(Например, 111111, Москва, ул. Московская, д. 1, кв. 1)</i>',
            reply_markup=inkb_order_cancel, disable_notification=True)
    else:
        await message.answer(
            f'Ошибка, номер телефона указан не правильно!', reply_markup=inkb_order_cancel, disable_notification=True)


async def client_order_step4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['order_address'] = message.text
        article = data['order_data'].split('_')[0]
        size = data['order_data'].split('_')[1]
        order_value = data['order_data'].split('_')[2]
        user_id = message.from_user.id
        order_date = message.date
        user_email = data['order_email']
        user_phone = data['order_phone']
        user_address = data['order_address']
        order = await client_requests.sql_add_order(article, user_id, order_date, order_value, user_email, user_phone,
                                                    user_address, size)
    inkb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=f'Запомнить данные', callback_data=f'm_y_{order}')).add(
        InlineKeyboardButton(text=f'Не запоминать данные', callback_data=f'm_n_{order}'))
    if order:
        await FSMorder.next()
        await message.answer(
            f'Могу я запомнить Ваши контактные данные для удобства последующих заказов?', reply_markup=inkb,
            disable_notification=True)
    else:
        await state.finish()
        await message.answer(text="К сожалению, товар закончился на складе", reply_markup=inkb_client_menu)


async def client_order_finish(callback: types.CallbackQuery, state: FSMContext):
    decis = callback.data.split("_")[1]
    order = callback.data.split("_")[2]
    async with state.proxy() as data:
        user_email = data['order_email']
        user_phone = data['order_phone']
        user_address = data['order_address']
        article = data['order_data'].split('_')[0]
        size = data['order_data'].split('_')[1]
        order_value = data['order_data'].split('_')[2]
    if decis == 'y':
        await client_requests.sql_add_client(callback.from_user.first_name, callback.from_user.id, user_phone,
                                             user_email, user_address)
    await state.finish()
    await callback.message.edit_text(
        f'Спасибо! Ваш заказ №{order} создан.\nВ ближайшее время с Вами свяжется администратор для уточнения деталей.',
        reply_markup=inkb_client_menu)
    await bot.send_message(admins[0],
                           f'Заказ №{order}\nАртикул {article}\nРазмер {size}\nСтоимость {order_value}\nТелефон {user_phone}\nПочта {user_email}\nАдрес {user_address}',
                           reply_markup=InlineKeyboardMarkup().add(
                               InlineKeyboardButton(text=f'Отменить', callback_data=f'o_cancel_{order}')).add(
                               InlineKeyboardButton(text=f'Подтвердить', callback_data=f'o_approve_{order}')))
    await callback.answer()


async def client_morder_finish(callback: types.CallbackQuery):
    user_data = await client_requests.sql_search_client(callback.from_user.id)
    article = callback.data.split("_")[1]
    user_id = callback.from_user.id
    order_date = callback.message.date
    order_value = callback.data.split("_")[3]
    user_email = user_data[4]
    user_phone = user_data[3]
    user_address = user_data[5]
    size = callback.data.split("_")[2]
    order = await client_requests.sql_add_order(article, user_id, order_date, order_value, user_email, user_phone,
                                                user_address, size)
    if order:
        await callback.message.edit_text(
            f'Спасибо! Ваш заказ №{order} создан.\nВ ближайшее время с Вами свяжется администратор для уточнения деталей.',
            reply_markup=inkb_client_menu)
        await callback.answer()
        await bot.send_message(admins[0],
                               f'Заказ №{order}\nАртикул {article}\nРазмер {size}\nСтоимость {order_value}\nТелефон {user_phone}\nПочта {user_email}\nАдрес {user_address}',
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(text=f'Отменить', callback_data=f'o_cancel_{order}')).add(
                                   InlineKeyboardButton(text=f'Подтвердить', callback_data=f'o_approve_{order}')))
    else:
        await callback.answer(text="К сожалению, товар закончился на складе", show_alert=True)



def reg_handlers_client_ao(dp: Dispatcher):
    dp.register_callback_query_handler(client_order_start, Text(startswith='order_'))
    dp.register_callback_query_handler(client_order_step1, state=FSMorder.order_data)
    dp.register_message_handler(client_order_step2, state=FSMorder.order_email)
    dp.register_message_handler(client_order_step3, state=FSMorder.order_phone)
    dp.register_message_handler(client_order_step4, state=FSMorder.order_address)
    dp.register_callback_query_handler(client_order_finish, state=FSMorder.order_memory)
    dp.register_callback_query_handler(client_morder_finish, Text(startswith='mord_'))
