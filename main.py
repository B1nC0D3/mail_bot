import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import commands, get_mail, settings
from states import Settings

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_TOKEN')


def register_commands_handlers(dp: Dispatcher):
    dp.register_message_handler(
        commands.cmd_start, commands='start', state='*')
    dp.register_message_handler(
        commands.cmd_cancel, commands='reset', state='*')
    dp.register_message_handler(
        commands.cmd_cancel,
        Text(equals='Сброс', ignore_case=True), state='*')
    dp.register_message_handler(commands.blank)


def regitster_get_mail_handlers(dp: Dispatcher):
    dp.register_message_handler(
        get_mail.get_mail, commands='get_mail', state=Settings.settings_done)
    dp.register_message_handler(
        get_mail.get_mail,
        Text(equals='Проверить почту', ignore_case=True),
        state=Settings.settings_done)


def register_settings_handlers(dp):
    dp.register_message_handler(
        settings.settings,
        commands='settings', state='*')
    dp.register_message_handler(
        settings.settings,
        Text(equals='Настройки', ignore_case=True), state='*')
    dp.register_message_handler(
        settings.get_mail_login,
        state=Settings.waiting_for_mail_login)
    dp.register_message_handler(
        settings.get_mail_password,
        state=Settings.waiting_for_mail_password)
    dp.register_message_handler(
        settings.get_mail_domain,
        state=Settings.waiting_for_mail_domen)


async def set_commands(bot: Bot):
    bot_commands = [
        BotCommand(command='/start', description='Запуск бота'),
        BotCommand(command='/reset', description='Сбросить настройки'),
        BotCommand(command='/get_mail',
                   description='Получить почту '
                               '(только при заполненных настройках)'),
        BotCommand(command='/settings', description='Настройки')
    ]
    await bot.set_my_commands(bot_commands)


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    regitster_get_mail_handlers(dp)
    register_commands_handlers(dp)
    register_settings_handlers(dp)
    await set_commands(bot)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
