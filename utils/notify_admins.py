import logging

from aiogram import Dispatcher

from data.config import admins
from utils.db_api.ie_commands import count_ie
from loguru import logger

from utils.db_api.users_commands import count_users


async def on_startup_notufy(dp: Dispatcher):
    for admin in admins:
        try:
            text = 'Бот запущен /run'
            await dp.bot.send_message(chat_id=admin, text=text)
        except Exception as err:
            logging.exception(err)


# отправляет сообщение админам о новом зарегистрированном пользователе
async def new_user_registration(dp: Dispatcher, username):
    count = await count_users()
    for admin in admins:
        try:
            await dp.bot.send_message(chat_id=admin, text=f'✅В бонусной программе зарегистрирован новый пользователь: '
                                                          f'username: @{username}\n'
                                                          f'🚹Всего пользователей: <b>{count}</b>')
        except Exception as err:
            logger.exception(err)


async def send_admins(dp: Dispatcher, text):
    for admin in admins:
        try:
            await dp.bot.send_message(chat_id=admin, text=text)
        except Exception as err:
            logger.exception(err)