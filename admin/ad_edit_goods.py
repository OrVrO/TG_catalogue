from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import inkb_admin_menu
from bot_create import bot
from sql import admin_requests, menu_requests


class FSMeditgoods(StatesGroup):
    item_article = State()
    item_new_data = State()


async def admin_edit_item_start(callback: types.CallbackQuery):
    article = callback.data.split("_")[1]
    prev_message1 = callback.message.message_id - 1
    prev_message2 = callback.message.message_id - 2
    prev_message = callback.message.message_id
    chat_id = callback.message.chat.id
    edit_good_list_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Артикул", callback_data=f'edit_article_{article}')).add(
        InlineKeyboardButton(text="Наименование", callback_data=f'edit_name_{article}')).add(
        InlineKeyboardButton(text="Описание", callback_data=f'edit_description_{article}')).add(
        InlineKeyboardButton(text="Цена", callback_data=f'edit_price_{article}')).add(
        InlineKeyboardButton(text="Фото 1", callback_data=f'edit_photo1_{article}')).add(
        InlineKeyboardButton(text="Фото 2", callback_data=f'edit_photo2_{article}')).add(
        InlineKeyboardButton(text="Количество", callback_data=f'warehouse_{article}')).add(
        InlineKeyboardButton(text="Каталог", callback_data=f'admin_catalog'))
    await bot.delete_message(chat_id, prev_message1)
    await bot.delete_message(chat_id, prev_message2)
    await bot.delete_message(chat_id, prev_message)
    await callback.message.answer(f'Пожалуйста, выберите поле для редактирования:', reply_markup=edit_good_list_kb)
    await callback.answer()


async def admin_edit_item_step1(callback: types.CallbackQuery):
    article = callback.data.split("_")[2]
    column = callback.data.split("_")[1]
    column_dict = {"article": 1, "name": 5, "description": 6, "price": 9, "photo1": 7, "photo2": 8}
    data_sql = await menu_requests.sql_find_article_good(article)
    now = data_sql[column_dict[column]]
    keyb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Внести новые данные", callback_data=f'editstep2_{article}_{column}')).add(
        InlineKeyboardButton(text="Отмена", callback_data=f'cancel'))
    await FSMeditgoods.item_article.set()
    await callback.message.edit_text(f'Артикул {article}\nТекущие данные:\n{now}\n', reply_markup=keyb)
    await callback.answer()


async def admin_edit_item_step2(callback: types.CallbackQuery, state: FSMContext):
    article = callback.data.split("_")[1]
    column = callback.data.split("_")[2]
    async with state.proxy() as data:
        data['item_article'] = [article, column]
    await FSMeditgoods.next()
    await callback.message.edit_text(f'Напишите новые данные или пришлите новое фото')
    await callback.answer()


async def admin_edit_item_step3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        column = data['item_article'][1]
        if column[:5] == 'photo':
            if 'text' in message:
                await message.answer(f'Нужно фото!')
            else:
                data['item_new_data'] = message.photo[0].file_id
                article = data['item_article'][0]
                column = data['item_article'][1]
                new_data = data['item_new_data']
                date = message.date
                user_id = message.from_user.id
                await admin_requests.sql_edit_item(article, column, new_data, date, user_id)
                await state.finish()
                await message.answer(f'Изменения внесены', reply_markup=inkb_admin_menu)
        else:
            if 'photo' in message:
                await message.answer(f'Нужен текст!')
            else:
                data['item_new_data'] = message.text
                article = data['item_article'][0]
                column = data['item_article'][1]
                new_data = data['item_new_data']
                date = message.date
                user_id = message.from_user.id
                await admin_requests.sql_edit_item(article, column, new_data, date, user_id)
                await state.finish()
                await message.answer(f'Изменения внесены', reply_markup=inkb_admin_menu)


def reg_handlers_admin_eg(dp: Dispatcher):
    dp.register_callback_query_handler(admin_edit_item_start, Text(startswith='editstart_'))
    dp.register_callback_query_handler(admin_edit_item_step1, Text(startswith='edit_'))
    dp.register_callback_query_handler(admin_edit_item_step2, Text(startswith='editstep2_'),
                                       state=FSMeditgoods.item_article)
    dp.register_message_handler(admin_edit_item_step3, content_types=['text', 'photo'],
                                state=FSMeditgoods.item_new_data)
