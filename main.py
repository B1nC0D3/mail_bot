from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from dotenv import load_dotenv
import os
import asyncio
from keys import main_keyboard
from get_mail import get_mail

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class Settings(StatesGroup):
    settings = State()
    waiting_for_mail_login = State()
    waiting_for_mail_password = State()
    waiting_for_mail_domen = State()


@dp.message_handler(commands='start')
async def cmd_start(message, state):
    await state.finish()
    await message.answer(
        'test message',
        reply_markup=main_keyboard,
    )
    await state.update_data(domain='test domain')
    test = await state.get_data()
    print(test['domain'])


@dp.message_handler(Text(equals='Проверить почту', ignore_case=True))
async def check_mail(message, state):
    mails = get_mail(1, 1, 1)
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

async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())