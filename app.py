from handlers.users.admin.start_stop import restart_parser, run_parser
from utils.db_api.ie_commands import reset_all_users_is_run
import aiocron


async def on_startup(dp):
    from loguru import logger
    logger.add("file.log", format="{time} {level} {message}", level="DEBUG", rotation="50 MB", compression="zip")

    import filters
    filters.setup(dp)
    import middlewares
    middlewares.setup(dp)

    from loader import db
    from utils.db_api.db_gino import on_startup
    # logger.info('Подключение к PostgreSQL')
    await on_startup(db)

    # print('Удаление базы данных')
    # await db.gino.drop_all()

    # logger.info('создание таблиц')
    await db.gino.create_all()
    # logger.info('Готово')

    # импортирует функцию, которая отправляет сообщение о запуске бота всем администраторам
    from utils.notify_admins import on_startup_notufy
    await on_startup_notufy(dp)

    # импортирует функцию, которая устанавливает команды бота
    from utils.set_bot_commands import set_default_commands
    await set_default_commands(dp)

    # выдает в консоль бот запущен
    logger.info("Бот запущен")

    # Создаем задачу, которая будет выполняться каждый день в 00:00
    # перезапуск бота
    # aiocron.crontab('1 0 * * *', func=restart_parser, start=True)  # в 00:01

if __name__ == '__main__':
    from aiogram import executor  # импортируем executor для запуска поллинга
    from handlers import dp  # из хендлеров импортируем dp

    executor.start_polling(dp, on_startup=on_startup)
