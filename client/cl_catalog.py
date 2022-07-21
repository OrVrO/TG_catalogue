from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_create import bot
from sql import menu_requests, client_requests


async def client_catalog(callback: types.CallbackQuery):
    catalog_level1 = InlineKeyboardMarkup()
    for i in await menu_requests.sql_show_menu1():
        catalog_level1.add(InlineKeyboardButton(text=i[0], callback_data=f'c_level1_{i[0]}'))
    await callback.message.answer(f'Выберите раздел?', reply_markup=catalog_level1, disable_notification=True)
    await callback.answer()


async def client_catalog_l2(callback: types.CallbackQuery):
    level1 = callback.data.split("_")[-1]
    catalog_level2 = InlineKeyboardMarkup()
    for i in await menu_requests.sql_show_menu2(level1=level1):
        catalog_level2.add(InlineKeyboardButton(text=i[0], callback_data=f'c_level2_{i[0]}_{level1}'))
    await callback.message.edit_text(f'Выберите раздел?', reply_markup=catalog_level2)
    await callback.answer()


async def client_catalog_l3(callback: types.CallbackQuery):
    level2 = callback.data.split("_")[2]
    level1 = callback.data.split("_")[3]
    catalog_level3 = InlineKeyboardMarkup()
    for i in await menu_requests.sql_show_menu3(level1, level2):
        catalog_level3.add(
            InlineKeyboardButton(text=i[0], callback_data=f'c_level3_{i[0]}_{level1}'))
    await callback.message.edit_text(f'Выберите раздел?', reply_markup=catalog_level3)
    await callback.answer()


async def client_show_item(callback: types.CallbackQuery):
    level3 = callback.data.split("_")[2]
    level1 = callback.data.split("_")[3]
    data_sql = await client_requests.sql_show_item_client(level1, level3)
    pages = len(data_sql)
    item = data_sql[0]
    media = types.MediaGroup()
    media.attach_photo(item[7], f'{item[5]}\n{item[1]}\n{item[9]}')
    media.attach_photo(item[8], f'{item[5]}\n{item[1]}\n{item[9]}')
    chat_id = callback.message.chat.id
    next_item_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Заказать товар', callback_data=f'order_{item[1]}_{item[9]}')).add(
        InlineKeyboardButton(text='Следующий', callback_data=f'c_next_{level1}_{level3}_0')).add(
        InlineKeyboardButton(text='Меню', callback_data=f'start'))
    prev_message = callback.message.message_id
    await bot.delete_message(chat_id, prev_message)
    await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
    await callback.message.answer(
        f'<b>{item[5]}</b> (арт. {item[1]})\n<i>{item[6]}</i>\nЦена: <b>{item[9]}</b> руб.\n<i>Страница 1 из {pages}</i>',
        reply_markup=next_item_kb, disable_notification=True)
    await callback.answer()


async def client_show_next_item(callback: types.CallbackQuery):
    level1 = callback.data.split("_")[2]
    level3 = callback.data.split("_")[3]
    index = int(callback.data.split("_")[4]) + 1
    data_sql = await client_requests.sql_show_item_client(level1, level3)
    pages = len(data_sql)
    if (index + 1) > pages:
        await callback.answer(text=f'В каталоге больше нет товаров', show_alert=True)
    else:
        item = data_sql[index]
        media = types.MediaGroup()
        media.attach_photo(item[7], f'{item[5]}\n{item[1]}\n{item[9]}')
        media.attach_photo(item[8], f'{item[5]}\n{item[1]}\n{item[9]}')
        chat_id = callback.message.chat.id
        next_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Заказать товар', callback_data=f'order_{item[1]}_{item[9]}')).row(
            InlineKeyboardButton(text='Предыдущий', callback_data=f'c_prev_{level1}_{level3}_{index - 1}'),
            InlineKeyboardButton(text='Следующий', callback_data=f'c_next_{level1}_{level3}_{index}')).row(
            InlineKeyboardButton(text="Каталог", callback_data=f'client_catalog'),
            InlineKeyboardButton(text='Меню', callback_data=f'start'))
        prev_message1 = callback.message.message_id - 1
        prev_message2 = callback.message.message_id - 2
        prev_message = callback.message.message_id
        await bot.delete_message(chat_id, prev_message1)
        await bot.delete_message(chat_id, prev_message2)
        await bot.delete_message(chat_id, prev_message)
        await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
        await callback.message.answer(
            f'<b>{item[5]}</b> (арт. {item[1]})\n<i>{item[6]}</i>\nЦена: <b>{item[9]}</b> руб.\n<i>Страница {index + 1} из {pages}</i>',
            reply_markup=next_item_kb, disable_notification=True)
        await callback.answer()


async def client_show_prev_item(callback: types.CallbackQuery):
    level1 = callback.data.split("_")[2]
    level3 = callback.data.split("_")[3]
    index = int(callback.data.split("_")[4])
    data_sql = await client_requests.sql_show_item_client(level1, level3)
    pages = len(data_sql)
    if index < 0:
        await callback.answer(text=f'В каталоге больше нет товаров', show_alert=True)
    else:
        item = data_sql[index]
        media = types.MediaGroup()
        media.attach_photo(item[7], f'{item[5]}\n{item[1]}\n{item[9]}')
        media.attach_photo(item[8], f'{item[5]}\n{item[1]}\n{item[9]}')
        chat_id = callback.message.chat.id
        next_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Заказать товар', callback_data=f'order_{item[1]}_{item[9]}')).row(
            InlineKeyboardButton(text='Предыдущий', callback_data=f'c_prev_{level1}_{level3}_{index - 1}'),
            InlineKeyboardButton(text='Следующий', callback_data=f'c_next_{level1}_{level3}_{index}')).row(
            InlineKeyboardButton(text="Каталог", callback_data=f'client_catalog'),
            InlineKeyboardButton(text='Меню', callback_data=f'start'))
        prev_message1 = callback.message.message_id - 1
        prev_message2 = callback.message.message_id - 2
        prev_message = callback.message.message_id
        await bot.delete_message(chat_id, prev_message1)
        await bot.delete_message(chat_id, prev_message2)
        await bot.delete_message(chat_id, prev_message)
        await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
        await callback.message.answer(
            f'<b>{item[5]}</b> (арт. {item[1]})\n<i>{item[6]}</i>\nЦена: <b>{item[9]}</b> руб.\n<i>Страница {index + 1} из {pages}</i>',
            reply_markup=next_item_kb, disable_notification=True)
        await callback.answer()


def reg_handlers_client_ca(dp: Dispatcher):
    dp.register_callback_query_handler(client_catalog, text="client_catalog")
    dp.register_callback_query_handler(client_catalog_l2, Text(startswith='c_level1_'))
    dp.register_callback_query_handler(client_catalog_l3, Text(startswith='c_level2_'))
    dp.register_callback_query_handler(client_show_item, Text(startswith='c_level3_'))
    dp.register_callback_query_handler(client_show_next_item, Text(startswith='c_next_'))
    dp.register_callback_query_handler(client_show_prev_item, Text(startswith='c_prev_'))
