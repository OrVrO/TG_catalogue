from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

admins = ['11111']  # admin's TG id

storage = MemoryStorage()

bot = Bot(token="1111111", parse_mode=types.ParseMode.HTML)  # TG bot token
dp = Dispatcher(bot, storage=storage)

email_login = '1111111@email.ru'  # bot`s email login
email_password = '111111'  # bot`s email password
email_server = 'smtp.yandex.ru'
admin_email = '222222@email.ru'  # admin's email
