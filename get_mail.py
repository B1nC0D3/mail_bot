import imaplib
import email
from email.header import decode_header
import base64
from bs4 import BeautifulSoup



def get_mail(mail, password, domain):
    imap = imaplib.IMAP4_SSL('imap.yandex.ru')
    imap.login(mail, password)
    mails = []
    numbers = get_mail_numbers(imap, domain)
    for number in numbers:
        mail_data = get_mail_data(imap, number)
        mails.append(mail_data)
    imap.close()
    return mails



def get_mail_numbers(imap, domain):
    imap.select('INBOX')
    numbers = imap.search(None, f'(UNSEEN HEADER FROM "{domain}")')[1][0].split()
    return numbers

def get_mail_data(imap, number):
    code, msg = imap.fetch(number, '(RFC822)')
    message = email.message_from_bytes(msg[0][1])
    subject = decode_header(message['Subject'])[0][0].decode()
    mail_from = decode_header(message['From'])[0][0]
    attachments = []
    for part in message.walk():
        if part.get_content_maintype() == 'application':
            filename = part.get_filename()
            filename = decode_header(filename)[0][0].decode()
            if not filename: filename = 'tmp.txt'
            fp = open(f'files/{filename}', 'wb')
            fp.write(part.get_payload(decode=1))
            fp.close
            attachments.append(f'files/{filename}')
        elif part.get_content_maintype() == 'text' and part.get_content_subtype() == 'html':
            html = base64.b64decode(part.get_payload()).decode()
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
