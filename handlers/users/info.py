from aiogram import types

from filters import IsPrivate
from loader import dp
from utils.db_api.ie_commands import get_user_data


@dp.message_handler(IsPrivate(), text="/info", )
async def command_data(message: types.Message):
    data = await get_user_data(message.from_user.id)
    for key, value in data.items():
        if key != 'время обновления':
            await message.answer(f"{key}: {value}")
