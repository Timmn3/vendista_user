import aiohttp
import asyncio
from bs4 import BeautifulSoup
from loguru import logger
from utils.db_api.ie_commands import change_last_time, get_last_time
from datetime import datetime
from loader import bot

from utils.db_api.users_commands import get_user_id_by_card_number, update_bonus


async def current_time_formatted():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d.%m.%Y %H:%M:%S")
    return formatted_time


async def compare_dates(date_str_pars, date_str_bd):
    # Преобразование строк в объекты datetime
    date_str_pars = datetime.strptime(date_str_pars, '%d.%m.%Y %H:%M:%S')
    date_str_bd = datetime.strptime(date_str_bd, '%d.%m.%Y %H:%M:%S')

    # Сравнение дат
    if date_str_pars > date_str_bd:
        return True
    else:
        return False


async def parse_amount_string(amount_str):
    try:

        # Удаляем два последних символа и заменяем запятую на точку
        amount_str_cleaned = amount_str.replace("\xa0", "").replace(" ", "")[:-2].replace(",", ".")
        # Преобразуем строку в тип float
        amount_float = float(amount_str_cleaned)
        return amount_float
    except ValueError:
        # Если возникла ошибка при преобразовании, например, из-за неправильного формата строки
        return None


stop_flag = False  # Глобальная переменная для управления циклом


class AsyncLoginSessionManager:
    instance = None  # Статическое поле для хранения экземпляра

    def __init__(self, login_url='https://p.vendista.ru/Auth/Login'):
        self.login_url = login_url
        self.session = None  # Инициализировать сеанс как Нет

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def login(self, login, password):
        async with self.session.get(self.login_url) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        verification_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

        auth_url = 'https://p.vendista.ru/Auth/Login'
        login_data = {
            '__RequestVerificationToken': verification_token,
            'returnUrl': '',
            'Login': login,
            'Password': password,
        }

        async with self.session.post(auth_url, data=login_data) as response:
            if response.ok:
                return True
            else:
                logger.error('Authentication failed!')
                return False

    async def get_bonuses_data(self, user_data):
        user_id = user_data['user_id']

        try:
            while not stop_flag:  # Проверяйте флаг перед каждой итерацией
                unique_card_numbers = set()

                for page_number in range(1, 2):
                    bonuses_url_page = f'https://p.vendista.ru/Bonuses?OrderByColumn=3&OrderDesc=True&PageNumber={page_number}&ItemsOnPage=200&FilterText='

                    async with self.session.get(bonuses_url_page) as response_bonuses:
                        html_bonuses_page = await response_bonuses.text()

                    soup_bonuses_page = BeautifulSoup(html_bonuses_page, 'html.parser')
                    rows = soup_bonuses_page.select('.catalog__body .row')

                    # текущее время
                    date_str_now = str(await current_time_formatted())
                    # время из БД последнего запроса
                    date_str_bd = await get_last_time(int(user_id))
                    date_str_bd = '11.12.2023 20:00:00'

                    for row in rows:
                        columns = row.select('.catalog__table_td')
                        if columns:
                            card_number = columns[1].text.strip()
                            bonus_balance = columns[3].text.strip()
                            sale_time = columns[4].text.strip()
                            unique_card_numbers.add(card_number)

                            # сравниваем время последнего обновления со временем последней покупки
                            if await compare_dates(sale_time, date_str_bd):
                                # смотрим у какого пользователя совпадает номер карты
                                user = await get_user_id_by_card_number(card_number)
                                if user:
                                    # отправляем сообщение пользователю
                                    await bot.send_message(user, f'бонусы 💳{card_number}: {bonus_balance}')
                                    # сохраняем количество бонусов в БД
                                    bonus = await parse_amount_string(bonus_balance)
                                    await update_bonus(user, bonus)

                    # сохраняем текущее время в БД
                    await change_last_time(user_id, date_str_now)
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f'Ошибка извлечения бонусных данных для User ID {user_id}!', e)

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance


async def stop_processing():
    global stop_flag
    stop_flag = True  # Установите флаг, чтобы остановить обработку


async def start_processing():
    global stop_flag
    stop_flag = False  # Установите флаг, чтобы начать обработку


async def process_user(user_data):
    async with AsyncLoginSessionManager() as async_session_manager:
        try:
            if await async_session_manager.login(user_data['login'], user_data['password']):
                await async_session_manager.get_bonuses_data(user_data)
        except asyncio.CancelledError:
            pass  # При необходимости обработайте исключение отмены.

        await stop_processing()  # Остановить обработку после выполнения задачи


async def parsing_main(users_data):
    tasks = [process_user(user_data) for user_data in users_data]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    users_data_ = [
        {'user_id': 5669831950, 'login': 'golana127@mail.ru', 'password': 'qrjyat'},
        {'user_id': 1009831950, 'login': 'rrrr@mail.ru', 'password': 'dddd'}
    ]

    asyncio.run(parsing_main(users_data_))
