from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from get_mail import get_mail


async def check_mail(message: Message, state: FSMContext):
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
        await message.answer('Новых писем нет!')
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
