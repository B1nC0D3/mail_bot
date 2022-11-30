from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, Message
from dotenv import load_dotenv
import os
import re
import imaplib
import asyncio
from keys import start_keyboard, main_keyboard
from get_mail import get_mail

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class Settings(StatesGroup):
    waiting_for_mail_login = State()
    waiting_for_mail_password = State()
    waiting_for_mail_domen = State()
    settings_done = State()


@dp.message_handler(commands='start', state='*')
async def cmd_start(message, state):
    await message.answer(
        'Привет! Бот создан для быстрой проверки почты не выходя из мессенджера. '
        'Сначала необходимо заполнить настройки в боте и включить доступ к почте по протоколу IMAP, '
        'после этого бот будет готов к использованию.',
        reply_markup=start_keyboard,
    )

@dp.message_handler(commands='reset', state='*')
@dp.message_handler(Text(equals='Сброс', ignore_case=True), state='*')
async def cmd_cancel(message: Message, state: FSMContext):
    await state.reset_state()
    await message.reply('Настройки сброшены')

@dp.message_handler(commands='get_mail', state=Settings.settings_done)
@dp.message_handler(Text(equals='Проверить почту', ignore_case=True), state=Settings.settings_done)
async def check_mail(message: Message, state:FSMContext):
    user_data = await state.get_data()
    mail_login = user_data.get('mail_login')
    mail_password = user_data.get('mail_password')
    domain = user_data.get('domain')
    try:
        mails = get_mail(mail_login, mail_password, domain)
    except Exception as e:
        await message.answer(f'Произошла ошибка {e}')
        return
 
    if len(mails) == 0:
        await message.answer(
            'Новых писем нет!'
        )
        return

    await message.answer(
        f'Вот письма с указанным доменом, всего их {len(mails)}'
    )
    for mail in mails:
        mail_from = mail.get('mail_from')
        subject = mail.get('subject')
        attachments = mail.get('attachments')
        mail_text = mail.get('mail_text')
        await message.answer(
            f'От: {mail_from}\n'
            f'Тема письма: {subject}\n'
            f'Вложений: {len(attachments)}\n'
            f'Текст:\n {mail_text}'
        )
        if len(attachments) > 0:
            for attachment in attachments:
                file = open(attachment, 'rb')
                await message.answer_document(file)
                file.close

@dp.message_handler(commands='settings', state='*')
@dp.message_handler(Text(equals='Настройки', ignore_case=True), state='*')
async def settings(message: Message, state: FSMContext):
    await message.answer('Введите яндекс почту в формате urname@yandex.ru')
    await state.set_state(Settings.waiting_for_mail_login.state)

@dp.message_handler(state=Settings.waiting_for_mail_login)
async def get_mail_login(message: Message, state: FSMContext):
    if not re.match(r'^[-\w\.]+@yandex.ru', message.text.lower()):
        await message.answer('Введите корректную почту')
        return
    await state.update_data(mail_login=message.text.lower())
    await state.set_state(Settings.waiting_for_mail_password.state)
    await message.answer('Введите пароль от почты')

@dp.message_handler(state=Settings.waiting_for_mail_password)
async def get_mail_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        imap = imaplib.IMAP4_SSL('imap.yandex.ru')
        imap.login(user_data['mail_login'], message.text)
        await state.update_data(mail_password=message.text)
        await state.set_state(Settings.waiting_for_mail_domen.state)
        await message.answer('Введите отслеживаемый домен без @')
    except Exception as e:
        await message.answer('Не удалось войти с указанными данными, проверьте настройки почты и правильность введенных данных')

@dp.message_handler(state=Settings.waiting_for_mail_domen)
async def get_mail_domain(message: Message, state: FSMContext):
    if not re.match(r'([-\w]+\.)+[-\w]{2,4}$', message.text.lower()):
        await message.answer('Введите корректный домен')
        return
    await state.update_data(domain=message.text.lower())
    await message.answer('Настройки успешно сохранены!', reply_markup=main_keyboard)
    await state.set_state(Settings.settings_done.state)

@dp.message_handler()
async def blank(message: Message):
    await message.answer('Сначала заполните настройки!')

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='/start', description='Запуск бота'),
        BotCommand(command='/reset', description='Сбросить настройки'),
        BotCommand(command='/get_mail', description='Получить почту (только при заполненных настройках)'),
        BotCommand(command='/settings', description='Настройки')
    ]
    await bot.set_my_commands(commands)

async def main():
    await set_commands(bot)
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())