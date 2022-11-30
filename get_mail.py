import base64
import email
from email.header import decode_header
from imaplib import IMAP4_SSL

from bs4 import BeautifulSoup

import exceptions


def get_mail(mail: str, password: str, domain: str) -> list:
    try:
        imap = IMAP4_SSL('imap.yandex.ru')
        imap.login(mail, password)
    except Exception:
        raise exceptions.LoginError('Не удалось присоедениться к серверу')
    mails = []
    numbers = get_mail_numbers(imap, domain)
    for number in numbers:
        mail_data = get_mail_data(imap, number)
        mails.append(mail_data)
    imap.close()
    return mails



def get_mail_numbers(imap: IMAP4_SSL, domain: str) -> list:
    imap.select('INBOX')
    numbers = imap.search(None, f'(UNSEEN HEADER FROM "{domain}")')[1][0].split()
    return numbers

def get_mail_data(imap: IMAP4_SSL, number: str) -> dict:
    code, msg = imap.fetch(number, '(RFC822)')
    if not code == 'OK':
        raise exceptions.MailDataError('Не удалось получить письмо')
    try:
        message = email.message_from_bytes(msg[0][1])
        subject = decode_header(message['Subject'])[0][0].decode()
        mail_from = decode_header(message['From'])[0][0]
    except Exception:
        raise exceptions.MailDataError('Не удалось расшифровать письмо')
    attachments = []
    for part in message.walk():
        if part.get_content_maintype() == 'application':
            filename = part.get_filename()
            try:
                filename = decode_header(filename)[0][0].decode()
            except Exception:
                raise exceptions.MailDataError('Не удалось расшифровать имя вложения')
            if not filename: 
                filename = 'tmp.txt'
            try:
                fp = open(f'files/{filename}', 'wb')
                fp.write(part.get_payload(decode=1))
                fp.close
            except Exception:
                raise exceptions.MailDataError('Не удалось записать файл')
            attachments.append(f'files/{filename}')
        elif part.get_content_maintype() == 'text' and part.get_content_subtype() == 'html':
            try:
                html = base64.b64decode(part.get_payload()).decode()
            except Exception:
                raise exceptions.MailDataError('Не удалось расшифровать текст письма')
            soup = BeautifulSoup(html, 'html.parser')
            tag = soup.body
            unsorted_mail_text = ''
            for string in tag.strings:
                unsorted_mail_text += string
            unsorted_mail_text = unsorted_mail_text.split()
            mail_text = ' '.join(unsorted_mail_text)
    return {
        'subject': subject,
        'mail_from': mail_from,
        'attachments': attachments,
        'mail_text': mail_text,
    }

