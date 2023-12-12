from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand('my_bonuses', 'Мои бонусы'),
        types.BotCommand('register', 'Регистрация'),
        types.BotCommand('sms_notifications', 'СМС уведомления'),
        types.BotCommand('change_phone', 'изменить номер телефона для СМС'),
        types.BotCommand('help', 'Помощь'),

    ])
