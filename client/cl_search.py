from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_create import bot
from sql import client_requests


class FSMsearch(StatesGroup):
    search_sex = State()
    search_cloth_type = State()
    search_size = State()


async def search_start(callback: types.CallbackQuery):
    sql_data = await client_requests.sql_search1('catalog_level1')
    inkb = InlineKeyboardMarkup()
    for i in sql_data:
        inkb.add(InlineKeyboardButton(text=i[0], callback_data=f'{i[0]}'))
    await FSMsearch.search_sex.set()
    await callback.message.answer(
        f'Пожалуйста, выберите категорию?',
        reply_markup=inkb.add(InlineKeyboardButton(text="Отмена", callback_data='cancel_client')),
        disable_notification=True)
    await callback.answer()


async def search_start_step1(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['search_sex'] = callback.data
    sql_data = await client_requests.sql_search2('catalog_level2', 'catalog_level1', callback.data)
    inkb = InlineKeyboardMarkup()
    for i in sql_data:
        inkb.add(InlineKeyboardButton(text=i[0], callback_data=f'{callback.data}_{i[0]}'))
    await FSMsearch.next()
    await callback.message.edit_text(
        f'Пожалуйста, выберите категорию?',
        reply_markup=inkb.add(InlineKeyboardButton(text="Отмена", callback_data='cancel_client')))
    await callback.answer()


async def search_start_step2(callback: types.CallbackQuery, state: FSMContext):
    cloth_type = callback.data.split("_")[1]
    sex = callback.data.split("_")[0]
    async with state.proxy() as data:
        data['search_cloth_type'] = cloth_type
    sql_data = await client_requests.sql_search3('size', 'catalog_level2', 'catalog_level1', cloth_type, sex)
    inkb = InlineKeyboardMarkup()
    for i in sql_data:
        inkb.add(InlineKeyboardButton(text=i[0], callback_data=f'{sex}_{cloth_type}_{i[0]}'))
    await FSMsearch.next()
    await callback.message.edit_text(
        f'Пожалуйста, выберите Ваш размер?',
        reply_markup=inkb.add(InlineKeyboardButton(text="Отмена", callback_data='cancel_client')))
    await callback.answer()


async def search_start_finish(callback: types.CallbackQuery, state: FSMContext):
    cloth_type = callback.data.split("_")[1]
    sex = callback.data.split("_")[0]
    size = callback.data.split("_")[2]
    async with state.proxy() as data:
        data['search_size'] = size
    await state.finish()
    sql_data = await client_requests.sql_search_item(sex, cloth_type, size)
    pages = len(sql_data)
    item = sql_data[0]
    media = types.MediaGroup()
    media.attach_photo(item[7], f'{item[5]}\n{item[1]}\n{item[9]}')
    media.attach_photo(item[8], f'{item[5]}\n{item[1]}\n{item[9]}')
    chat_id = callback.message.chat.id
    next_item_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Заказать товар', callback_data=f'order_{item[1]}_{item[9]}')).add(
        InlineKeyboardButton(text='Следующий', callback_data=f'sn_{sex}_{cloth_type}_{size}_0')).add(
        InlineKeyboardButton(text='Меню', callback_data=f'start'))
    prev_message = callback.message.message_id
    await bot.delete_message(chat_id, prev_message)
    await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
    await callback.message.answer(
        f'<b>{item[5]}</b> (арт. {item[1]})\n<i>{item[6]}</i>\nЦена: <b>{item[9]}</b> руб.\n<i>Страница 1 из {pages}</i>',
        reply_markup=next_item_kb, disable_notification=True)
    await callback.answer()


async def search_next_item(callback: types.CallbackQuery):
    cloth_type = callback.data.split("_")[2]
    sex = callback.data.split("_")[1]
    size = callback.data.split("_")[3]
    index = int(callback.data.split("_")[4]) + 1
    sql_data = await client_requests.sql_search_item(sex, cloth_type, size)
    pages = len(sql_data)
    if (index + 1) > pages:
        await callback.answer(text=f'Больше нет товаров заданного размера', show_alert=True)
    else:
        item = sql_data[index]
        media = types.MediaGroup()
        media.attach_photo(item[7], f'{item[5]}\n{item[1]}\n{item[9]}')
        media.attach_photo(item[8], f'{item[5]}\n{item[1]}\n{item[9]}')
        chat_id = callback.message.chat.id
        next_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Заказать товар', callback_data=f'order_{item[1]}_{item[9]}')).row(
            InlineKeyboardButton(text='Предыдущий', callback_data=f'sp_{sex}_{cloth_type}_{size}_{index - 1}'),
            InlineKeyboardButton(text='Следующий', callback_data=f'sn_{sex}_{cloth_type}_{size}_{index}')).row(
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


async def search_prev_item(callback: types.CallbackQuery):
    cloth_type = callback.data.split("_")[2]
    sex = callback.data.split("_")[1]
    size = callback.data.split("_")[3]
    index = int(callback.data.split("_")[4])
    sql_data = await client_requests.sql_search_item(sex, cloth_type, size)
    pages = len(sql_data)
    if index < 0:
        await callback.answer(text=f'Больше нет товаров заданного размера', show_alert=True)
    else:
        item = sql_data[index]
        media = types.MediaGroup()
        media.attach_photo(item[7], f'{item[5]}\n{item[1]}\n{item[9]}')
        media.attach_photo(item[8], f'{item[5]}\n{item[1]}\n{item[9]}')
        chat_id = callback.message.chat.id
        next_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text='Заказать товар', callback_data=f'order_{item[1]}_{item[9]}')).row(
            InlineKeyboardButton(text='Предыдущий', callback_data=f'sp_{sex}_{cloth_type}_{size}_{index - 1}'),
            InlineKeyboardButton(text='Следующий', callback_data=f'sn_{sex}_{cloth_type}_{size}_{index}')).row(
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


def reg_handlers_client_se(dp: Dispatcher):
    dp.register_callback_query_handler(search_start, text='client_search')
    dp.register_callback_query_handler(search_start_step1, state=FSMsearch.search_sex)
    dp.register_callback_query_handler(search_start_step2, state=FSMsearch.search_cloth_type)
    dp.register_callback_query_handler(search_start_finish, state=FSMsearch.search_size)
    dp.register_callback_query_handler(search_next_item, Text(startswith='sn_'))
    dp.register_callback_query_handler(search_prev_item, Text(startswith='sp_'))
