from celery import Celery
from django.core.mail import send_mail
from dailyfresh import settings

# 创建celery客户端
# 参数1：自定义
# 参数2：中间人
app = Celery('dailyfresh', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_mail(username, email, token):
    """发送激活邮件"""
    subject = '天天生鲜用户激活'  # 标题 不能为空 否则会报错
    message = ''  # 邮件的正文（纯文本） 如果html_message有值那么message会被覆盖掉
    sender = settings.EMAIL_FROM  # 发件人
    receivers = [email]
    # 邮件正文（html样式）
    html_message = '<h2>尊敬的 %s, 感谢注册天天生鲜</h2>' \
                   '<p>请点击此链接激活您的帐号: ' \
                   '<a href="http://127.0.0.1:8000/users/active/%s">' \
                   'http://127.0.0.1:8000/users/active/%s</a>' \
                   % (username, token, token)
    send_mail(subject, message,  sender, receivers, html_message=html_message)
    send_mail(subject, message, sender, receivers,
              html_message=html_message)