from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keys import start_keyboard


async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        'Привет! Бот создан для быстрой проверки '
        'почты не выходя из мессенджера. '
        'Сначала необходимо заполнить настройки в боте '
        'и включить доступ к почте по протоколу IMAP, '
        'после этого бот будет готов к использованию.',
        reply_markup=start_keyboard,
    )


async def cmd_cancel(message: Message, state: FSMContext):
    await state.reset_state()
    await message.reply('Настройки сброшены')


async def blank(message: Message):
    await message.answer('Сначала заполните настройки!')
