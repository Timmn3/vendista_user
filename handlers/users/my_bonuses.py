from aiogram import types
from aiogram.utils.deep_linking import get_start_link
from loader import dp
from utils.db_api.users_commands import get_bonus


@dp.message_handler(text="/my_bonuses")
async def my_bonuses(message: types.Message):
    bonus = await get_bonus(message.from_user.id)
    if bonus:
        await message.answer(f'У Вас {bonus} бонусов✅')
    else:
        await message.answer(f'Совершите оплату в кофеаппарате, что бы появились бонусы!')
