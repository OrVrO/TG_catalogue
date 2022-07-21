from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import inkb_client_menu
from bot_create import bot, admins
from sql import admin_requests


async def admin_order_approve(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[2]
    admin_id = str(callback.from_user.id)
    data_sql = await admin_requests.sql_order_approve(order_id, admin_id)
    if data_sql:
        await callback.message.answer(f'Заказ {order_id} подтверждён!', reply_markup=InlineKeyboardMarkup()
                                      .add(InlineKeyboardButton(text='Заказы', callback_data='admin_orders'))
                                      .add(InlineKeyboardButton(text='Меню', callback_data='start')))
        await bot.send_message(data_sql[4],
                               f'Ваш заказ {order_id} подтверждён администратором!'
                               f'\nВ ближайшее время с Вами свяжутся для уточнения деталей.',
                               reply_markup=inkb_client_menu)
    else:
        await callback.answer(text=f'Заказ {order_id} не существует!', show_alert=True)
    await callback.answer()


async def admin_order_cancel(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[2]
    user_id = str(callback.from_user.id)
    data_sql = await admin_requests.sql_order_cancel(order_id, user_id)
    if data_sql:
        if str(user_id) in admins:
            await callback.message.answer(f'Заказ {order_id} отменён!', reply_markup=InlineKeyboardMarkup()
                                      .add(InlineKeyboardButton(text='Заказы', callback_data='admin_orders'))
                                      .add(InlineKeyboardButton(text='Меню', callback_data='start')))
        await bot.send_message(data_sql[1][4], data_sql[0], reply_markup=inkb_client_menu)
    else:
        await callback.answer(text=f'Заказ {order_id} не существует!', show_alert=True)
    await callback.answer()


async def admin_order_ready(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[2]
    admin_id = str(callback.from_user.id)
    data_sql = await admin_requests.sql_order_ready(order_id, admin_id)
    if data_sql:
        await callback.message.answer(f'Заказ {order_id} исполнен!', reply_markup=InlineKeyboardMarkup()
                                      .add(InlineKeyboardButton(text='Заказы', callback_data='admin_orders'))
                                      .add(InlineKeyboardButton(text='Меню', callback_data='start')))
        await bot.send_message(data_sql[4], text=f'Ваш заказ  {order_id} исполнен!'
                                                 f'\nСпасибо что Вы с нами!', reply_markup=inkb_client_menu)
    else:
        await callback.answer(text=f'Заказ {order_id} не существует!', show_alert=True)
    await callback.answer()


async def admin_orders_menu(callback: types.CallbackQuery):
    if str(callback.from_user.id) in admins:
        await callback.message.edit_text(f'Пожалуйста, выберите пункт меню:',
                                         reply_markup=InlineKeyboardMarkup()
                                         .add(InlineKeyboardButton(text='Новые заказы', callback_data='admin_ord_new'))
                                         .add(
                                             InlineKeyboardButton(text='Текущие заказы', callback_data='admin_ord_app'))
                                         .add(InlineKeyboardButton(text='Исполненные заказы',
                                                                   callback_data='admin_ord_rdy'))
                                         .add(InlineKeyboardButton(text='Меню',
                                                                   callback_data='start')))
    else:
        await callback.answer(text='Нужны права администраторва', show_alert=True)
    await callback.answer()


async def admin_orders_list(callback: types.CallbackQuery):
    param = callback.data.split("_")[2]
    data_sql = await admin_requests.sql_list_orders(param)
    inkb_list = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Назад", callback_data='admin_orders'))
    for i in data_sql:
        inkb_list.add(InlineKeyboardButton(text=f'№{i[1]} от {i[4]}', callback_data=f'adord_edstat_{i[1]}'))
    await callback.message.edit_text(f'Список заказов ниже:', reply_markup=inkb_list)
    await callback.answer()


async def admin_edit_order_status(callback: types.CallbackQuery):
    order_id = callback.data.split("_")[2]
    data_sql = await admin_requests.sql_find_order(order_id)
    if 'Подтверждён' in str(data_sql[10]):
        inkb = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Отменить', callback_data=f'o_cancel_{order_id}')) \
            .add(InlineKeyboardButton(text=f'Исполнен', callback_data=f'o_ready_{order_id}')) \
            .add(InlineKeyboardButton(text=f'Меню', callback_data='start'))\
            .add(InlineKeyboardButton(text=f'Заказы', callback_data='admin_orders'))
    elif 'Исполнен' in str(data_sql[10]):
        inkb = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Меню', callback_data='start'))\
            .add(InlineKeyboardButton(text=f'Заказы', callback_data='admin_orders'))
    else:
        inkb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text=f'Подтвердить', callback_data=f'o_approve_{order_id}')) \
            .add(InlineKeyboardButton(text=f'Отменить', callback_data=f'o_cancel_{order_id}')) \
            .add(InlineKeyboardButton(text=f'Исполнен', callback_data=f'o_ready_{order_id}')) \
            .add(InlineKeyboardButton(text=f'Меню', callback_data='start'))\
            .add(InlineKeyboardButton(text=f'Заказы', callback_data='admin_orders'))
    await callback.message.edit_text(f'Пожалуйста, выберите статус для заказа {data_sql[1]}'
                                     f'\nАртикул товара: {data_sql[2]}'
                                     f'\nРазмер: {data_sql[3]}'
                                     f'\nСтоимость: {data_sql[9]}'
                                     f'\nЗаказчик: {data_sql[4]}'
                                     f'\nТелефон: {data_sql[6]}'
                                     f'\nE-mail: {data_sql[5]}'
                                     f'\nАдрес: {data_sql[7]}'
                                     f'\nДата: {data_sql[8]}', reply_markup=inkb)
    await callback.answer()


def reg_handlers_admin_or(dp: Dispatcher):
    dp.register_callback_query_handler(admin_order_approve, Text(startswith='o_approve_'))
    dp.register_callback_query_handler(admin_order_cancel, Text(startswith='o_cancel_'))
    dp.register_callback_query_handler(admin_order_ready, Text(startswith='o_ready_'))
    dp.register_callback_query_handler(admin_orders_menu, text='admin_orders')
    dp.register_callback_query_handler(admin_orders_list, text='admin_ord_new')
    dp.register_callback_query_handler(admin_orders_list, text='admin_ord_app')
    dp.register_callback_query_handler(admin_orders_list, text='admin_ord_rdy')
    dp.register_callback_query_handler(admin_edit_order_status, Text(startswith='adord_edstat_'))
