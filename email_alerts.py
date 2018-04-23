import smtplib
from email.mime.text import MIMEText
import socket

class Email_alarm:
    def __init__(self):
        self.msg_from = '575548935@qq.com'  # 发送方邮箱
        self.passwd = 'dfdgxobhmvaebcba'  # 填入发送方邮箱的授权码
        self.msg_to = '575548935@qq.com'  # 收件人邮箱
        self.subject = socket.gethostname()

    def send_mail(self, content):
        msg = MIMEText(content)
        msg['Subject'] = self.subject
        msg['From'] = self.msg_from
        msg['To'] = self.msg_to
        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(self.msg_from, self.passwd)
            s.sendmail(self.msg_from, self.msg_to, msg.as_string())
            print("发送成功")
        except:
            print("发送失败")
        finally:
            s.quit()


if __name__ == "__main__":
    email_alarm = Email_alarm()
    email_alarm.send_mail("Hello!")
    # print(socket.gethostname())






