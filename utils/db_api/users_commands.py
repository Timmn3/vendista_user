from asyncpg import UniqueViolationError
from loguru import logger

from utils.db_api.db_gino import db
from utils.db_api.shemas.users import Users


async def add_user(user_id: int, tg_first_name: str, tg_last_name: str, name: str, card_number: str, phone_number: str,
                   status: str, bonus: float, number_ie: int, sms_status: bool):
    try:
        user = Users(user_id=user_id, tg_first_name=tg_first_name, tg_last_name=tg_last_name,
                     name=name, card_number=card_number, phone_number=phone_number,
                     status=status, bonus=bonus, number_ie=number_ie, sms_status=sms_status)
        await user.create()
    except UniqueViolationError:
        logger.exception('Ошибка при добавлении пользователя')


async def select_user(user_id):
    """ Выбрать пользователя"""
    try:
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        return user
    except Exception as e:
        logger.exception(f'Ошибка при выборе пользователя: {e}')


async def update_card_number(user_id: int, new_card_number: str):
    """ Изменить номер карты пользователя """
    try:
        # Проверяем, существует ли пользователь
        if await Users.query.where(Users.user_id == user_id).gino.first():
            # Если пользователь существует, обновляем номер карты
            await Users.update.values(card_number=new_card_number).where(Users.user_id == user_id).gino.status()
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить номер карты.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении номера карты пользователя: {e}')


async def update_phone_number(user_id: int, new_phone_number: str):
    """ Изменить номер телефона пользователя """
    try:
        # Проверяем, существует ли пользователь
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            # Если пользователь существует, обновляем номер телефона
            await Users.update.values(phone_number=new_phone_number).where(Users.user_id == user_id).gino.status()

        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить номер телефона.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении номера телефона пользователя: {e}')


async def update_sms_status(user_id: int, new_sms_status: bool):
    """ Изменить статус SMS пользователя """
    try:
        # Проверяем, существует ли пользователь
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            # Если пользователь существует, обновляем статус SMS
            await Users.update.values(sms_status=new_sms_status).where(Users.user_id == user_id).gino.status()

        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить статус SMS.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении статуса SMS пользователя: {e}')


async def get_sms_status(user_id: int):
    """ Получить статус SMS пользователя """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем статус SMS
            return user.sms_status
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить статус SMS.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении статуса SMS пользователя: {e}')
        return None  # or raise an exception if you prefer


async def delete_user(user_id: int):
    """ Удалить пользователя из базы данных """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Удаляем пользователя
            await user.delete()

            info = f"Пользователь с ID {user_id} успешно удален."
        else:
            info = f"Пользователь с ID {user_id} не найден."

        return info
    except Exception as e:
        logger.exception(f'Ошибка при удалении пользователя: {e}')


async def get_number_ie(user_id: int):
    """ Получить значение number_ie для пользователя """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем значение number_ie
            return user.number_ie
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить значение number_ie.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении значения number_ie для пользователя: {e}')
        return None  # or raise an exception if you prefer


async def get_user_id_by_card_number(card_number: str):
    """ Получить user_id по номеру карты """
    try:
        # Выбираем пользователя по номеру карты
        user = await Users.query.where(Users.card_number == card_number).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем user_id
            return user.user_id
        else:
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении user_id по номеру карты: {e}')
        return None  # or raise an exception if you prefer


async def update_bonus(user_id: int, new_bonus: float):
    """ Изменить значение бонусов пользователя """
    try:
        # Проверяем, существует ли пользователь
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        if user:
            # Если пользователь существует, обновляем значение бонусов
            await Users.update.values(bonus=new_bonus).where(Users.user_id == user_id).gino.status()
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно обновить значение бонусов.")
    except Exception as e:
        logger.exception(f'Ошибка при изменении значения бонусов пользователя: {e}')


async def get_bonus(user_id: int):
    """ Получить значение бонусов пользователя """
    try:
        # Выбираем пользователя
        user = await Users.query.where(Users.user_id == user_id).gino.first()

        # Проверяем, существует ли пользователь
        if user:
            # Возвращаем значение бонусов
            return user.bonus
        else:
            logger.warning(f"Пользователь с ID {user_id} не найден. Невозможно получить значение бонусов.")
            return None  # or raise an exception if you prefer
    except Exception as e:
        logger.exception(f'Ошибка при получении значения бонусов пользователя: {e}')
        return None  # or raise an exception if you prefer


async def count_users():
    try:
        # Используем асинхронный метод count для подсчета пользователей
        user_count = await Users.query.gino.count().gino.scalar()

        return user_count
    except Exception as e:
        logger.exception(f'Ошибка при подсчете пользователей: {e}')
        return None