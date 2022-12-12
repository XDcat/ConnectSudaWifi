import smtplib
import requests
import re
from email.mime.text import MIMEText


def get_ip():
    """
    获取ip
    注意此 ip 并不一定是本地的 ip。
    当你将路由器连接到网络中，其他设备再通过路由器来连接网络。
    此时 ip 将会是路由器 ip，且只有路由器需要登录。
    在路由器登陆后，其他设备无需登录。
    """
    url = "http://10.9.1.3/?isReback=1"
    response = requests.get(url)
    ip_mo = re.search("(?:v46ip|v4ip)=.*?(\d+\.\d+\.\d+\.\d+)", response.text)
    ip = ip_mo.group(1)
    return ip


def send_mail():
    # 设置服务器所需信息
    mail_host = "pop.111.com"
    mail_user = "zenglianjie@111.com"
    mail_pass = "Pk2TbTYRwUh69vrV"
    sender = "zenglianjie@111.com"
    receivers = ["514269236@qq.com", ]

    # 设置email信息
    # 邮件内容设置
    message = MIMEText('ip:%s\n不知道什么原因，您的机器已经启动，请检查是否有任务中断，请尽快处理！' % get_ip(), 'plain',
                       'utf-8')
    # 邮件主题
    message['Subject'] = 'logger: 刀片机已经重新启动'
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = ",".join(receivers)

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP()
        # 连接到服务器
        smtpObj.connect(mail_host, 25)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误import smtplib


if __name__ == "__main__":
    send_mail()
