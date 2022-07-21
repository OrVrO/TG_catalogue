from aiogram.utils import executor
from sql import start_database
from admin import ad_catalog, ad_main_menu, ad_add_goods, ad_edit_goods, ad_orders
from client import cl_catalog, cl_main_menu, cl_add_order, cl_search
from bot_create import dp


async def on_startup(_):
    print("Бот онлайн")
    start_database.sql_start()


ad_main_menu.reg_handlers_admin_mm(dp)
ad_catalog.reg_handlers_admin_ca(dp)
ad_add_goods.reg_handlers_admin_ag(dp)
ad_edit_goods.reg_handlers_admin_eg(dp)
ad_orders.reg_handlers_admin_or(dp)
cl_main_menu.reg_handlers_client_mm(dp)
cl_catalog.reg_handlers_client_ca(dp)
cl_add_order.reg_handlers_client_ao(dp)
cl_search.reg_handlers_client_se(dp)


async def on_shutdown(_):
    print("Бот оффлайн")


executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
