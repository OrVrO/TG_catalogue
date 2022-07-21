from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

inkb_level1 = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data='cancel'))
with open("catalog_scheme.json", "r", encoding="utf-8") as read_file:
    data = list(json.load(read_file)['Level1'])
    data.sort()
    for i in data:
        inkb_level1.add(InlineKeyboardButton(text=i, callback_data=i))

inkb_level2 = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data='cancel'))
with open("catalog_scheme.json", "r", encoding="utf-8") as read_file:
    data = list(json.load(read_file)['Level2'])
    data.sort()
    for i in data:
        inkb_level2.add(InlineKeyboardButton(text=i, callback_data=i))

inkb_level3 = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data='cancel'))
with open("catalog_scheme.json", "r", encoding="utf-8") as read_file:
    data = list(json.load(read_file)['Level3'])
    data.sort()
    for i in data:
        inkb_level3.add(InlineKeyboardButton(text=i, callback_data=i))

inkb_admin_menu = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Добавить новый товар", callback_data='add_goods')).add(
    InlineKeyboardButton(text="Каталог", callback_data='admin_catalog')).add(
    InlineKeyboardButton(text="Найти артикул", callback_data='admin_find_item')).add(
    InlineKeyboardButton(text="Заказы", callback_data='admin_orders')).add(
    InlineKeyboardButton(text="Прислать отчет в Excel", callback_data='admin_send_report_xlsx'))

inkb_add_goods_cancel = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data='cancel'))