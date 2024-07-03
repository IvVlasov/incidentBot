import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import settings


def send_mail(subject, text, files=None, server=settings.SMTP_SERVER):
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USER
    msg['To'] = settings.SMTP_SEND_TO
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    smtp = smtplib.SMTP_SSL(host=server, port=465)
    smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    smtp.sendmail(settings.SMTP_USER, settings.SMTP_SEND_TO, msg.as_string())
    smtp.close()


def send_claim(chat_id, data, path_list):
    subject = settings.MSGS['mail_subject'].format(record_id=data['record_id'])
    text = settings.MSGS['mail_claim']
    text = text.format(chat_id=chat_id,
                       type=data['type'],
                       descr=data['descr'],
                       phone=data['phone'],
                       contact=data.get('contact', '-'))
    send_mail(subject, text, path_list)
