from aiogram import types
from loader import dp
from data.config import admins, ADMIN_IE
from parser.parser import parsing_main, stop_processing, start_processing
from utils.db_api.ie_commands import get_user_data


@dp.message_handler(text='/run', chat_id=admins)
async def run(message: types.Message):
    users_data = await get_user_data(ADMIN_IE)
    await start_processing()
    await message.answer('Запущено!')
    # запустить процесс для всех пользователей
    await parsing_main(users_data)


@dp.message_handler(text='/stop', chat_id=admins)
async def stop(message: types.Message):
    await stop_processing()
    await message.answer('Остановлено!')


