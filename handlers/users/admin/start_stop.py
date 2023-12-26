from aiogram import types
from loader import dp
import asyncio
from data.config import admins, ADMIN_IE
from parser.parser import parsing_main, stop_processing, start_processing
from utils.db_api.ie_commands import get_user_data
from loguru import logger

# Флаг для управления ежечасным перезапуском
restart_enabled = True


async def hourly_task():
    global restart_enabled
    while True:
        if restart_enabled:
            users_data = await get_user_data(ADMIN_IE)
            await start_processing()
            await parsing_main(users_data)
        await asyncio.sleep(3600)  # Подождать 1 час


@dp.message_handler(text='/run', chat_id=admins)
async def run(message: types.Message):
    global restart_enabled
    restart_enabled = True
    asyncio.create_task(hourly_task())  # Use asyncio loop instead of dp.loop
    await message.answer('Запущено!')


@dp.message_handler(text='/stop', chat_id=admins)
async def stop(message: types.Message):
    global restart_enabled
    restart_enabled = False
    await stop_processing()
    await message.answer('Остановлено!')


async def restart_parser():
    await stop_processing()
    await asyncio.sleep(5)
    users_data = await get_user_data(ADMIN_IE)
    await start_processing()
    await parsing_main(users_data)


async def run_parser():
    await asyncio.sleep(5)
    user_data = await get_user_data(ADMIN_IE)
    for admin in admins:
        try:
            text = f'Работает для {ADMIN_IE}'
            await dp.bot.send_message(chat_id=admin, text=text)
        except Exception as err:
            await dp.bot.send_message(chat_id=admin, text=f'Ошибка запуска для {ADMIN_IE}')
            logger.exception(err)
    await parsing_main(user_data)
