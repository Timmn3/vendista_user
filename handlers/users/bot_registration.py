""" Регистрация нового автомата """

import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from filters import IsPrivate
from handlers.users.my_qrcode import send_qr_code
from keyboards.default import cancel_registration, kb_sms
from loader import dp
from parser.verification import main_authorize
from states import Registration
from utils.db_api.ie_commands import change_email_and_password, get_sms_status_ie
from utils.db_api.users_commands import update_card_number, update_phone_number, update_sms_status, get_number_ie, \
    get_user_id_by_card_number, get_card_number_by_user_id
from utils.notify_admins import send_admins, new_user_registration


@dp.message_handler(text='Отменить регистрацию')
async def cast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Отменено')


@dp.message_handler(text=['Регистрация', '/register'])
async def register(message: types.Message):
    user_id = int(message.from_user.id)
    cards = await get_card_number_by_user_id(user_id)
    if cards == '0':
        await message.answer('Для понимания какой картой Вы оплачиваете кофе, введите первые две цифры своей карты, '
                             'потом 4 звездочки и последние четыре цифры карты, \nнапример: 22****7192')
        await message.answer('Номер карты:', reply_markup=cancel_registration)
        await Registration.number.set()
    else:
        await message.answer(f'Вы зарегистрированы!\nВаши карты: \n{cards}\n'
                             f'Если Вы хотите добавить или удалить карту выберите в меню пункт /cards')


@dp.message_handler(state=Registration.number)
async def get_number(message: types.Message, state: FSMContext):
    number = message.text
    if number == "Отменить регистрацию":
        await state.finish()
        await message.answer('Отменено')
    else:
        user_id = int(message.from_user.id)

        if validate_number(number):
            # сохраняем номер карты в БД
            await update_card_number(user_id, number)
            await state.finish()

            user_id_ie = await get_number_ie(message.from_user.id)
            # смотрим подключена ли СМС уведомление в кофейне
            if await get_sms_status_ie(user_id_ie):
                await message.answer('👍Отлично!')
                await message.answer('Хотите получать СМС уведомления?', reply_markup=kb_sms)
            else:
                await message.answer(
                    '👍Отлично! Регистрация завершена, теперь вы будете получать уведомления о балансе '
                    'бонусов в telegram боте!📲\n'
                    '1 бонус = 1 рублю! Вы можете выбрать напиток и приложить карту как обычно к терминалу!'
                    'При достаточном наличии бонусов деньги не списываются и у Вас будет написано "бесплатная продажа"!')
                # отправляем админам нового пользователя
                await new_user_registration(dp=dp, username=message.from_user.username)

        else:
            await message.answer('Некорректный ввод. Пример: 22****7192:', reply_markup=cancel_registration)


def validate_number(number):
    pattern = r'^\d{2}\*\*\*\*\d{4}$'
    return re.match(pattern, number) is not None


@dp.message_handler(text='да')
async def register(message: types.Message):
    await message.answer('На какой номер Вы хотели бы получать СМС уведомления?')
    await message.answer('Введите номер телефона в формате 89886654411:', reply_markup=cancel_registration)
    await Registration.phone.set()


@dp.message_handler(state=Registration.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if phone == "Отменить регистрацию":
        await state.finish()
        await message.answer('Отменено')
    else:
        user_id = int(message.from_user.id)
        if validate_phone(phone):
            # сохраняем номер карты в БД
            await update_phone_number(user_id, phone)
            await update_sms_status(user_id, True)
            await message.answer('Отлично! Теперь Вы будете получать уведомления в telegram и по СМС\n'
                                 'Если вы не хотите получать СМС, в меню выберите пункт "СМС уведомления"')
            # отправляем админам нового пользователя
            await new_user_registration(dp=dp, username=message.from_user.username)
            await state.finish()
        else:
            await message.answer('Некорректный ввод. Пример: 89886654411:',
                                 reply_markup=cancel_registration)


def validate_phone(phone):
    pattern = r'^89\d{9}$'
    return re.match(pattern, phone) is not None


@dp.message_handler(text='нет')
async def register(message: types.Message, state: FSMContext):
    await message.answer('👍Отлично! Регистрация завершена, теперь вы будете получать уведомления о балансе '
                         'бонусов в telegram боте!📲')
    # отправляем админам нового пользователя
    await new_user_registration(dp=dp, username=message.from_user.username)
    await state.finish()
