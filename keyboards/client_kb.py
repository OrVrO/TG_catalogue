from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inkb_client_menu = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Каталог", callback_data='client_catalog')).add(
    InlineKeyboardButton(text="Поиск по параметрам", callback_data='client_search')).add(
    InlineKeyboardButton(text="Заказы", callback_data='client_orders')).add(
    InlineKeyboardButton(text="Оплата и доставка", callback_data='client_terms')).add(
    InlineKeyboardButton(text="Связаться с нами", callback_data='client_contact'))

inkb_order_cancel = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data='cancel_client'))