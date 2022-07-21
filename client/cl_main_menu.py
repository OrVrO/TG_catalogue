from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_create import bot
from keyboards import inkb_client_menu
from sql import client_requests, menu_requests


async def cancel_fsm_client(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.edit_text(f'Отменил', reply_markup=inkb_client_menu)
    await callback.answer()


async def client_orders(callback: types.CallbackQuery):
    data_sql_orders = await client_requests.sql_show_orders_client(callback.from_user.id)
    if data_sql_orders:
        pages = len(data_sql_orders)
        item_orders = data_sql_orders[0]
        item_good = await menu_requests.sql_find_article_good(item_orders[2])
        media = types.MediaGroup()
        media.attach_photo(item_good[7], f'{item_good[5]}\n{item_good[1]}\n{item_good[9]}')
        media.attach_photo(item_good[8], f'{item_good[5]}\n{item_good[1]}\n{item_good[9]}')
        chat_id = callback.message.chat.id
        next_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Отменить заказ', callback_data=f'o_cancel_{item_orders[1]}')).add(
            InlineKeyboardButton(text='Далее', callback_data=f'ord_next_0')).add(
            InlineKeyboardButton(text='Меню', callback_data=f'start'))
        prev_message = callback.message.message_id
        if 'Подтверждён' in str(item_orders[10]):
            status = f"Заказ подтверждён администратором"
        else:
            status = f"Заказ в обработке"
        await bot.delete_message(chat_id, prev_message)
        await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
        await callback.message.answer(
            f'Заказ №{item_orders[1]}\n<b>{item_good[5]}</b> (арт. {item_good[1]})\n<i>{item_good[6]}</i>\nРазмер: <b>{item_orders[3]}</b>\nЦена: <b>{item_orders[9]}</b> руб.\nСтатус: {status}\n<i>Страница 1 из {pages}</i>',
            reply_markup=next_item_kb, disable_notification=True)
    else:
        await callback.message.answer(f'У Вас нет заказов.', disable_notification=True)
    await callback.answer()


async def client_order_next(callback: types.CallbackQuery):
    data_sql_orders = await client_requests.sql_show_orders_client(callback.from_user.id)
    pages = len(data_sql_orders)
    index = int(callback.data.split("_")[2]) + 1
    if (index + 1) > pages:
        await callback.answer(text=f'У Вас больше нет заказов', show_alert=True)
    else:
        item_orders = data_sql_orders[index]
        item_good = await menu_requests.sql_find_article_good(item_orders[2])
        media = types.MediaGroup()
        media.attach_photo(item_good[7], f'{item_good[5]}\n{item_good[1]}\n{item_good[9]}')
        media.attach_photo(item_good[8], f'{item_good[5]}\n{item_good[1]}\n{item_good[9]}')
        chat_id = callback.message.chat.id
        next_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Отменить заказ', callback_data=f'o_cancel_{item_orders[1]}')).add(
            InlineKeyboardButton(text='Далее', callback_data=f'ord_next_{index}')).add(
            InlineKeyboardButton(text='Назад', callback_data=f'ord_prev_{index}')).add(
            InlineKeyboardButton(text='Меню', callback_data=f'start'))
        if 'Подтверждён' in str(item_orders[10]):
            status = f"Заказ подтверждён администратором"
        else:
            status = f"Заказ в обработке"
        prev_message1 = callback.message.message_id - 1
        prev_message2 = callback.message.message_id - 2
        prev_message = callback.message.message_id
        await bot.delete_message(chat_id, prev_message1)
        await bot.delete_message(chat_id, prev_message2)
        await bot.delete_message(chat_id, prev_message)
        await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
        await callback.message.answer(
            f'Заказ №{item_orders[1]}\n<b>{item_good[5]}</b> (арт. {item_good[1]})\n<i>{item_good[6]}</i>\nРазмер: <b>{item_orders[3]}</b>\nЦена: <b>{item_orders[9]}</b> руб.\nСтатус: {status}\n<i>Страница {index + 1} из {pages}</i>',
            reply_markup=next_item_kb, disable_notification=True)
        await callback.answer()


async def client_order_prev(callback: types.CallbackQuery):
    data_sql_orders = await client_requests.sql_show_orders_client(callback.from_user.id)
    pages = len(data_sql_orders)
    index = int(callback.data.split("_")[2]) - 1
    if index < 0:
        await callback.answer(text=f'У Вас больше нет заказов', show_alert=True)
    else:
        item_orders = data_sql_orders[index]
        item_good = await menu_requests.sql_find_article_good(item_orders[2])
        media = types.MediaGroup()
        media.attach_photo(item_good[7], f'{item_good[5]}\n{item_good[1]}\n{item_good[9]}')
        media.attach_photo(item_good[8], f'{item_good[5]}\n{item_good[1]}\n{item_good[9]}')
        chat_id = callback.message.chat.id
        next_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Отменить заказ', callback_data=f'o_cancel_{item_orders[1]}')).add(
            InlineKeyboardButton(text='Далее', callback_data=f'ord_next_{index}')).add(
            InlineKeyboardButton(text='Назад', callback_data=f'ord_prev_{index}')).add(
            InlineKeyboardButton(text='Меню', callback_data=f'start'))
        if 'Подтверждён' in str(item_orders[10]):
            status = f"Заказ подтверждён администратором"
        else:
            status = f"Заказ в обработке"
        prev_message1 = callback.message.message_id - 1
        prev_message2 = callback.message.message_id - 2
        prev_message = callback.message.message_id
        await bot.delete_message(chat_id, prev_message1)
        await bot.delete_message(chat_id, prev_message2)
        await bot.delete_message(chat_id, prev_message)
        await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
        await callback.message.answer(
            f'Заказ №{item_orders[1]}\n<b>{item_good[5]}</b> (арт. {item_good[1]})\n<i>{item_good[6]}</i>\nРазмер: <b>{item_orders[3]}</b>\nЦена: <b>{item_orders[9]}</b> руб.\nСтатус: {status}\n<i>Страница {index + 1} из {pages}</i>',
            reply_markup=next_item_kb, disable_notification=True)
        await callback.answer()


async def client_terms(callback: types.CallbackQuery):
    await callback.message.edit_text(f'Оплата происходит <b>наличными</b> курьеру при получении заказа или в нашем магазине.'
                                     f'\nМы можем отправить товар за Ваш счёт любой выбранной Вами транспортной компанией в любой город.'
                                     f'\nВ пределах нашего города заказ на сумму свыше 10000 руб. привезёт курьер, бесплатно.', reply_markup=inkb_client_menu)
    await callback.answer()


async def client_contact(callback: types.CallbackQuery):
    await callback.message.edit_text(f'Связаться с нами можно по телефону +79876543210'
                                     f'\nИли по электронной почте test@test.com'
                                     f'\nИли найти нас в магазине по адресу: Москва,<code>ул. Московская, дом 1</code>', reply_markup=inkb_client_menu)
    await callback.answer()


def reg_handlers_client_mm(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_fsm_client, text='cancel_client', state="*")
    dp.register_callback_query_handler(client_orders, text="client_orders")
    dp.register_callback_query_handler(client_order_next, Text(startswith="ord_next_"))
    dp.register_callback_query_handler(client_order_prev, Text(startswith="ord_prev_"))
    dp.register_callback_query_handler(client_terms, text="client_terms")
    dp.register_callback_query_handler(client_contact, text="client_contact")
