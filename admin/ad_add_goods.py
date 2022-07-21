from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import inkb_level1
from keyboards import inkb_level2
from keyboards import inkb_level3
from keyboards import inkb_add_goods_cancel
from sql import admin_requests, menu_requests


class FSMaddgoods(StatesGroup):
    item_article = State()
    item_photo1 = State()
    item_photo2 = State()
    item_description = State()
    item_name = State()
    item_price = State()
    item_catalog1 = State()
    item_catalog2 = State()
    item_catalog3 = State()


class FSMwarehouse(StatesGroup):
    wrhs_article = State()
    wrhs_size = State()
    wrhs_quantity = State()


async def add_goods_step1(callback: types.CallbackQuery):
    await FSMaddgoods.item_article.set()
    await callback.message.edit_text(f'Артикул товара?', reply_markup=inkb_add_goods_cancel)
    await callback.answer()


async def add_goods_step2(message: types.Message, state: FSMContext):
    if await menu_requests.sql_find_article_good(message.text):
        await message.answer(f'Этот артикул уже есть в базе!')
    else:
        async with state.proxy() as data:
            data['item_article'] = message.text
        await FSMaddgoods.next()
        await message.answer(f'Первое фото?', reply_markup=inkb_add_goods_cancel, disable_notification=True)


async def add_goods_step3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['item_photo1'] = message.photo[0].file_id
    await FSMaddgoods.next()
    await message.answer(f'Второе фото?', reply_markup=inkb_add_goods_cancel, disable_notification=True)


async def add_goods_step4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['item_photo2'] = message.photo[0].file_id
    await FSMaddgoods.next()
    await message.answer(f'Описание товара?', reply_markup=inkb_add_goods_cancel, disable_notification=True)


async def add_goods_step5(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['item_description'] = message.text
    await FSMaddgoods.next()
    await message.answer(f'Название товара?', reply_markup=inkb_add_goods_cancel, disable_notification=True)


async def add_goods_step6(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['item_name'] = message.text
    await FSMaddgoods.next()
    await message.answer(f'Цена товара?', reply_markup=inkb_add_goods_cancel, disable_notification=True)


async def add_goods_step7(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['item_price'] = message.text
    await FSMaddgoods.next()
    await message.answer(f'Выберите категорию уровня 1?', reply_markup=inkb_level1, disable_notification=True)


async def add_goods_step8(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['item_catalog1'] = callback.data
    await FSMaddgoods.next()
    await callback.message.edit_text(f'Выберите категорию уровня 2?', reply_markup=inkb_level2)
    await callback.answer()


async def add_goods_step9(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['item_catalog2'] = callback.data
    await FSMaddgoods.next()
    await callback.message.edit_text(f'Выберите категорию уровня 3?', reply_markup=inkb_level3)
    await callback.answer()


async def add_goods_finish(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    date_add = callback.message.date
    async with state.proxy() as data:
        data['item_catalog3'] = callback.data
        item_article = data['item_article']
        catalog_level1 = data['item_catalog1']
        catalog_level2 = data['item_catalog2']
        catalog_level3 = data['item_catalog3']
        name = data['item_name']
        description = data['item_description']
        photo1 = data['item_photo1']
        photo2 = data['item_photo2']
        price = data['item_price']
        await admin_requests.sql_add_goods(item_article, catalog_level1, catalog_level2, catalog_level3, name,
                                           description,
                                           photo1, photo2,
                                           price, date_add, user_id)
    await state.finish()
    await callback.message.edit_text(f'Добавили успешно!', reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Изменить количество", callback_data=f'warehouse_{item_article}')).add(
        InlineKeyboardButton(text="Добавить новый товар", callback_data='add_goods')).add(
        InlineKeyboardButton(text="Каталог", callback_data='admin_catalog')).add(
        InlineKeyboardButton(text="Найти артикул", callback_data='admin_find_item')))
    await callback.answer()


async def admin_warehouse_start(callback: types.CallbackQuery):
    article = callback.data.split("_")[1]
    data_sql = await menu_requests.sql_find_article_warehouse(article)
    await FSMwarehouse.wrhs_article.set()
    inkb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Да', callback_data=f'{article}')).add(
        InlineKeyboardButton(text='Нет', callback_data=f'cancel'))
    message = ''
    for i in data_sql:
        size = str(i[2])
        quantity = str(i[3])
        text = f'Размер {size} в количестве {quantity}\n'
        message += text
    if data_sql:
        await callback.message.edit_text(f'<b>Артикул {article}</b>\n{message}\nИзменить количество?',
                                         reply_markup=inkb)
    else:
        await callback.message.edit_text(f'Артикул {article}, нет товаров на складе.\n Добавить товары?',
                                         reply_markup=inkb)
    await callback.answer()


async def admin_warehouse_step1(callback: types.CallbackQuery, state: FSMContext):
    article = callback.data
    async with state.proxy() as data:
        data['wrhs_article'] = article
    await FSMwarehouse.next()
    await callback.message.edit_text(f'Введите размер?', reply_markup=inkb_add_goods_cancel)
    await callback.answer()


async def admin_warehouse_step2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['wrhs_size'] = message.text
    await FSMwarehouse.next()
    await message.answer(f'Введите количество?', reply_markup=inkb_add_goods_cancel, disable_notification=True)


async def admin_warehouse_finish(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['wrhs_quantity'] = message.text
        article = data['wrhs_article']
        size = data['wrhs_size']
        quantity = data['wrhs_quantity']
        date = message.date
        user_id = message.from_user.id
        await admin_requests.sql_add_item_warehouse(article, size, quantity, date, user_id)
    await state.finish()
    inkb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Да', callback_data=f'warehouse_{article}')).add(
        InlineKeyboardButton(text="Добавить новый товар", callback_data='add_goods')).add(
        InlineKeyboardButton(text="Каталог", callback_data='admin_catalog')).add(
        InlineKeyboardButton(text="Найти артикул", callback_data='admin_find_item'))
    await message.answer(f'Изменили количество. Ещё один размер?', reply_markup=inkb, disable_notification=True)


def reg_handlers_admin_ag(dp: Dispatcher):
    dp.register_callback_query_handler(add_goods_step1, text='add_goods', state=None)
    dp.register_message_handler(add_goods_step2, state=FSMaddgoods.item_article)
    dp.register_message_handler(add_goods_step3, content_types=['photo'], state=FSMaddgoods.item_photo1)
    dp.register_message_handler(add_goods_step4, content_types=['photo'], state=FSMaddgoods.item_photo2)
    dp.register_message_handler(add_goods_step5, state=FSMaddgoods.item_description)
    dp.register_message_handler(add_goods_step6, state=FSMaddgoods.item_name)
    dp.register_message_handler(add_goods_step7, state=FSMaddgoods.item_price)
    dp.register_callback_query_handler(add_goods_step8, state=FSMaddgoods.item_catalog1)
    dp.register_callback_query_handler(add_goods_step9, state=FSMaddgoods.item_catalog2)
    dp.register_callback_query_handler(add_goods_finish, state=FSMaddgoods.item_catalog3)
    dp.register_callback_query_handler(admin_warehouse_start, Text(startswith='warehouse_'))
    dp.register_callback_query_handler(admin_warehouse_step1, state=FSMwarehouse.wrhs_article)
    dp.register_message_handler(admin_warehouse_step2, state=FSMwarehouse.wrhs_size)
    dp.register_message_handler(admin_warehouse_finish, state=FSMwarehouse.wrhs_quantity)
