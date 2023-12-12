import requests
from bs4 import BeautifulSoup

# URL для страницы авторизации
login_url = 'https://p.vendista.ru/Auth/Login'

# Создаем сессию для обработки куков
session = requests.Session()

# Отправляем GET-запрос для получения страницы и извлечения токена
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')
verification_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

# URL и данные для аутентификации
auth_url = 'https://p.vendista.ru/Auth/Login'
login_data = {
    '__RequestVerificationToken': verification_token,
    'returnUrl': '',
    'Login': 'golana127@mail.ru',
    'Password': '1',
}

# Отправляем POST-запрос для аутентификации
response = session.post(auth_url, data=login_data)

# URL для перехода после успешной авторизации
bonuses_url = 'https://p.vendista.ru/Bonuses'

# Отправляем GET-запрос для перехода по новому URL
response_bonuses = session.get(bonuses_url)

# Проверяем результат перехода
try:
    print("Переход по URL успешен!")

    # Извлекаем данные из таблицы
    soup_bonuses = BeautifulSoup(response_bonuses.text, 'html.parser')

    # Находим количество страниц
    pagination = soup_bonuses.find('div', class_='pagination')
    if pagination:
        last_page = int(pagination.find_all('a')[-2].text)
    else:
        last_page = 1

    # Множество для хранения уникальных номеров карт
    unique_card_numbers = set()

    # Итерация по всем страницам
    for page_number in range(1, 2):  # last_page + 1):
        # Обновляем URL с номером страницы
        bonuses_url_page = f'https://p.vendista.ru/Bonuses?OrderByColumn=3&OrderDesc=True&PageNumber={page_number}&ItemsOnPage=200&FilterText='
        response_bonuses = session.get(bonuses_url_page)

        # Извлекаем данные из таблицы на текущей странице
        soup_bonuses_page = BeautifulSoup(response_bonuses.text, 'html.parser')
        rows = soup_bonuses_page.select('.catalog__body .row')

        for row in rows:
            columns = row.select('.catalog__table_td')
            if columns:
                card_number = columns[1].text.strip()
                bonus_balance = columns[3].text.strip()
                last_sale_time = columns[4].text.strip()

                # Добавляем номер карты в множество
                unique_card_numbers.add(card_number)

                print(f"Номер карты: {card_number}, Баланс: {bonus_balance}, Время последней продажи: {last_sale_time}")

    # Выводим общее количество уникальных карт
    # print(f"Общее количество уникальных карт: {len(unique_card_numbers)}")
    # print(f"Общее количество страниц: {last_page}")

except Exception as e:
    print('Аутентификация не прошла!', e)
