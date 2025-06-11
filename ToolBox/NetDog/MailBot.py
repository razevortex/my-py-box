import subprocess as sp
import smtplib


class MailBot(object):
    def __init__(self, email:str, app_key:str):
        self.email = email
        self.app_key = app_key

    def server(self):
        srv = smtplib.SMTP("smtp.gmail.com", 587)
        srv.starttls()
        srv.login(self.email, self.app_key)
        return srv

    def send(self, to, message):
        self.server().sendmail(self.email, to, message)


if __name__ == '__main__':
    mailbot = MailBot('address@gmail.com', 'appkey')
    msg = 'Subject: Test\n\nBody'
    mailbot.send('razevortex@googlemail.com', msg)

