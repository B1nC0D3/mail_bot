import imaplib
import re

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keys import main_keyboard
from states import Settings


async def settings(message: Message, state: FSMContext):
    await message.answer('Введите яндекс почту в формате urname@yandex.ru')
    await state.set_state(Settings.waiting_for_mail_login.state)


async def get_mail_login(message: Message, state: FSMContext):
    if not re.match(r'^[-\w\.]+@yandex.ru', message.text.lower()):
        await message.answer('Введите корректную почту')
        return
    await state.update_data(mail_login=message.text.lower())
    await state.set_state(Settings.waiting_for_mail_password.state)
    await message.answer('Введите пароль от почты')


async def get_mail_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        imap = imaplib.IMAP4_SSL('imap.yandex.ru')
        imap.login(user_data['mail_login'], message.text)
        await state.update_data(mail_password=message.text)
        await state.set_state(Settings.waiting_for_mail_domen.state)
        await message.answer('Введите отслеживаемый домен без @')
    except Exception:
        await message.answer('Не удалось войти с указанными данными, '
                             'проверьте настройки почты '
                             'и правильность введенных данных')


async def get_mail_domain(message: Message, state: FSMContext):
    if not re.match(r'([-\w]+\.)+[-\w]{2,4}$', message.text.lower()):
        await message.answer('Введите корректный домен')
        return
    await state.update_data(domain=message.text.lower())
    await message.answer(
        'Настройки успешно сохранены!', reply_markup=main_keyboard)
    await state.set_state(Settings.settings_done.state)
