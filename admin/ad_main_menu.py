from aiogram import types, Dispatcher
import aiogram.utils.markdown as fmt
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import inkb_admin_menu
from keyboards import inkb_client_menu
from bot_create import bot, admins, admin_email
from sql import menu_requests, admin_requests
import bot_xlsx


class FSMfinditem(StatesGroup):
    item_article = State()


async def admin_delete_item(message: types.Message):
    article = message.text.split(" ")[1]
    user_id = str(message.from_user.id)
    if user_id in admins:
        result = await admin_requests.sql_delete_item(article)
        if result:
            await message.answer(f'Товар {article} удалён из базы!', reply_markup=inkb_admin_menu)
        else:
            await message.answer(f'Товара {article} нет в базе!', reply_markup=inkb_admin_menu)
    else:
        await message.answer(f'У Вас нет прав на это действие!')


async def hello_admin(message: types.Message):
    user_id = str(message.from_user.id)
    user_first_name = message.from_user.first_name
    hello = f"Привет <b>{fmt.quote_html(user_first_name)}</b>!" \
            f"\n"f"Пожалуйста, выбери действие."
    if user_id in admins:
        await message.answer(hello, reply_markup=inkb_admin_menu)
    else:
        await message.answer(hello, reply_markup=inkb_client_menu)


async def hello_cb(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    user_first_name = callback.from_user.first_name
    hello = f"Привет <b>{fmt.quote_html(user_first_name)}</b>!" \
            f"\n"f"Пожалуйста, выбери действие."
    if user_id in admins:
        await callback.message.answer(hello, reply_markup=inkb_admin_menu)
    else:
        await callback.message.answer(hello, reply_markup=inkb_client_menu)
    await callback.answer()


async def cancel_fsm(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.edit_text(f'Отменили', reply_markup=inkb_admin_menu)
    await callback.answer()


async def admin_find_item1(callback: types.CallbackQuery):
    await callback.message.edit_text(f'Напишите артикул предмета для редактирования',
                                     reply_markup=InlineKeyboardMarkup().add(
                                         InlineKeyboardButton(text="Отмена", callback_data='cancel')))
    await FSMfinditem.item_article.set()
    await callback.answer()


async def admin_find_item2(message: types.Message, state: FSMContext):
    prev_message = message.message_id
    chat_id = message.chat.id
    item = await menu_requests.sql_find_article_good(message.text)
    if item:
        media = types.MediaGroup()
        media.attach_photo(item[7], f'{item[5]}\n{item[1]}\n{item[9]}')
        media.attach_photo(item[8], f'{item[5]}\n{item[1]}\n{item[9]}')
        edit_item_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text="Редактировать товар", callback_data=f'editstart_{item[1]}')).add(
            InlineKeyboardButton(text="Каталог", callback_data=f'admin_catalog')).add(
            InlineKeyboardButton(text="Изменить количество", callback_data=f'warehouse_{item[1]}'))
        await state.finish()
        await bot.delete_message(chat_id, prev_message)
        await bot.send_media_group(chat_id=chat_id, media=media, disable_notification=True)
        await message.answer(f'<b>{item[5]}</b> (арт. {item[1]})\n<i>{item[6]}</i>\nЦена: <b>{item[9]}</b> руб.',
                             reply_markup=edit_item_kb, disable_notification=True)
    else:
        await message.answer(f'Такого артикула в базе нет!',
                             reply_markup=InlineKeyboardMarkup().add(
                                 InlineKeyboardButton(text="Отмена", callback_data='cancel')))


async def admin_send_report_xlsx(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    inkb = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton(text="Заказы текущие", callback_data='email_orders_order*status_Подтверждён')) \
        .add(InlineKeyboardButton(text="Заказы исполненные", callback_data='email_orders_order*status_Исполнен')) \
        .add(InlineKeyboardButton(text="Список товаров", callback_data='email_good')) \
        .add(InlineKeyboardButton(text="Список клиентов", callback_data='email_clients')) \
        .add(InlineKeyboardButton(text="Остатки на складе", callback_data='email_clientgoods')) \
        .add(InlineKeyboardButton(text="Меню", callback_data='start'))
    if user_id in admins:
        await callback.message.edit_text(text=f'Пожалуйста, выберите отчёт для отправки на электронную почту',
                                         reply_markup=inkb)
        await callback.answer()
    else:
        await callback.answer(text=f'У Вас недостаточно прав', show_alert=True)


async def admin_email_callback(callback: types.CallbackQuery):
    len_callback = len(callback.data.split("_"))
    file_name = 'report.xlsx'
    table_name = callback.data.split("_")[1]
    if len_callback == 2:
        await bot_xlsx.make_excel(table_name, file_name)
        await bot_xlsx.send_email(file_name)
        await callback.answer(text=f'Файл отправлен на электронную почту {admin_email}', show_alert=True)
    else:
        column = callback.data.split("_")[2]
        param = callback.data.split("_")[3]
        if '*' in column:
            column = column.replace('*', '_')
        await bot_xlsx.make_excel(table_name, file_name, column, param)
        await bot_xlsx.send_email(file_name)
        await callback.answer(text=f'Файл отправлен на электронную почту {admin_email}', show_alert=True)


def reg_handlers_admin_mm(dp: Dispatcher):
    dp.register_message_handler(admin_delete_item, Text(startswith='Удалить'))
    dp.register_message_handler(hello_admin)
    dp.register_callback_query_handler(hello_cb, text='start')
    dp.register_callback_query_handler(cancel_fsm, text='cancel', state="*")
    dp.register_callback_query_handler(admin_find_item1, text="admin_find_item")
    dp.register_message_handler(admin_find_item2, content_types=['text'], state=FSMfinditem.item_article)
    dp.register_callback_query_handler(admin_send_report_xlsx, text='admin_send_report_xlsx')
    dp.register_callback_query_handler(admin_email_callback, Text(startswith='email_'))
