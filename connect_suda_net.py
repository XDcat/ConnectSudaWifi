#!/usr/bin/env python
# coding: utf-8
import logging
import logging.config
import socket
import re
import json
# 第三方类
import requests

# 登录信息
# user information
user = "20214227076"
passwd = "Zlj1784470039"
# email information
mailhost = "pop.111.com"
fromaddr = "zenglianjie@111.com"
toaddrs = ["514269236@qq.com", ]
subject = "logger: 自动连接苏大网"
credentials = ("zenglianjie@111.com", "Pk2TbTYRwUh69vrV")  # 用户，密码
# log 控制台输出等级
level_log_console = "INFO"

# log 配置
# log config
default_config = {
    "version": 1,  # 目前只有 1 有效，用于以后兼容性
    "incremental": False,  # 是否在运行中时修改配置, 默认 False
    "disable_existing_loggers": True,  # 是否禁用任何非根的所有 Logger, 默认 False
    "formatters": {  # 格式化生成器(格式器)
        "default": {
            "format": "%(name)s %(asctime)s [%(filename)s %(funcName)s()] <%(levelname)s>: %(message)s",
        },
        "brief": {
            "format": "%(name)s [%(funcName)s()] <%(levelname)s>: %(message)s",
        },
        "mail": {
            "format": "名称: %(name)s\n时间: %(asctime)s\n文件: %(filename)s %(funcName)s() \n等级: <%(levelname)s>\n\n%(message)s",
        }
    },
    "filters": {},  # 过滤器，需要自定义类，一般不会用到
    "handlers": {
        "console": {  # 控制台
            "class": "logging.StreamHandler",
            "formatter": "brief",
            "level": level_log_console,
            "stream": "ext://sys.stdout",
        },
        "file_detail": {  # 输出到文件
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "level": "DEBUG",
            "filename": "/home/zlj/script/connect_suda_net.log",  # 必选, 文件名称
            "encoding": "utf8",
            "maxBytes": 10485760,  # 日志文件最大个数 1024B * 1024 * 10 = 10MB
            "backupCount": 1,  # 日志文件最大个数
        },
        "mail": {  # 邮件
            "class": "logging.handlers.SMTPHandler",
            "formatter": "mail",
            "mailhost": mailhost,
            "fromaddr": fromaddr,
            "toaddrs": toaddrs,
            "subject": subject,
            "credentials": credentials,  # 用户，密码
        }
    },
    "loggers": {
        "simple": {
            "level": "DEBUG",
            "handlers": ["console", "file_detail"],
            "propagate": False,  # 是否传给父级
        },
        "email": {
            "level": "DEBUG",
            "handlers": ["console", "file_detail", "mail"],
            "propagate": False,  # 是否传给父级
        }
    },
}
# 启动配置文件
logging.config.dictConfig(default_config)

logger = logging.getLogger("simple")
logger.info("logger 配置完毕")
email_logger = logging.getLogger("email")
logger.info("email logger 配置完毕")


# email_logger.info("emial logger 配置完毕(如果邮件频繁，请在邮箱中设置收信规则)")


# 函数

## 辅助函数


def decode_unicode(s):
    # 将 unicode 字符串解码
    return s.encode('utf8').decode('unicode_escape')


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
    logger.debug("ip 为 %s", ip)
    return ip


def parse_msg(msg):
    logger.debug("解析 msg: %s", msg)
    msg_json_text = re.search("\{.*\}", msg)
    res = json.loads(msg_json_text.group(0))
    return res


## 状态
# 从状态中可以知道对应 ip 对应的用户是谁，而注销只需要知道 ip 和用户。所以可以通过扫描所有 ip 的状态，注销任何指定用户或者指定 ip 。


def get_status(ip=None):
    if ip is None:
        ip = get_ip()
    logger.debug("获取 %s 的在线状态, 是否为本机 %s", ip, ip is not None)
    url = "http://10.9.1.3:801/eportal/"
    payload = {
        "c": "Portal",
        "a": "online_list",
        "callback": "dr1002",
        "wlan_user_ip": ip,
    }
    response = requests.get(url, params=payload)
    logger.debug(response)
    logger.debug(decode_unicode(response.text))
    response_text = decode_unicode(response.text)
    msg = parse_msg(response_text)
    logger.debug("%s 状态信息为 %s", ip, msg)
    return msg


def is_login(ip=None):
    if ip is None:
        ip = get_ip()
    msg = get_status(ip)
    res = int(msg["result"]) == 1
    logger.debug("%s 是否处于登录状态：%s", ip, res)
    return res


def get_overall():
    """整体状态"""
    res = {}
    res["ip"] = get_ip()
    res["是否登录"] = is_login()
    res["状态信息"] = get_status()
    logger.info("ip: %s", res["ip"])
    logger.info("是否登录: %s", res["是否登录"])
    return res


## 登录
# 
# 当前状态
# 1. 未登录，尝试登录
#     * 登录失败 dr1003({"result":"0","msg":"******","ret_code":1})
#         * msg == bGRhcCBhdXRoIGVycm9y, 账户密码错误
#     * 登录成功 dr1003({"result":"1","msg":"认证成功"})
# 2. 登录后，尝试登录
#     * 登录失败 dr1003({"result":"0","msg":"","ret_code":2}) 


def login(user, passwd, is_keep=False, ip=None):
    url = "http://10.9.1.3:801/eportal/"
    if ip is None:
        ip = get_ip()
    keep_flag = "0" if is_keep else "b"  # 是否保持登录
    payload = {
        "c": "Portal",
        "a": "login",
        "callback": "dr1003",
        "login_method": "1",
        "user_account": ",{},{}".format(keep_flag, user),
        "user_password": passwd,
        "wlan_user_ip": ip,
        #     "wlan_user_ipv6": "",
        #     "wlan_user_mac": "000000000000",
        #     "wlan_ac_ip": "",
        #     "wlan_ac_name": "",
        #     "jsVersion": "3.3.3",
    }
    response = requests.get(url, params=payload)
    logger.debug(response)
    logger.debug(decode_unicode(response.text))
    response_text = decode_unicode(response.text)
    msg = parse_msg(response_text)
    res = int(msg["result"]) == 1
    logger.debug("登录%s", "成功" if res else "失败")
    return res, msg


## 注销


def logout(user, ip=None):
    url = "http://10.9.1.3:801/eportal/"
    if ip is None:
        ip = get_ip()
    # 解绑-针对保持登陆的用户
    payload = {
        "c": "Portal",
        "a": "unbind_mac",
        "callback": "dr1003",
        "user_account": user,
        "wlan_user_ip": ip,
    }
    response = requests.get(url, params=payload)
    logger.debug(response)
    logger.debug(decode_unicode(response.text))

    # 推出登录
    payload = {
        "c": "Portal",
        "a": "logout",
        "callback": "dr1004",
        "login_method": "1",
        "ac_logout": "1",
        "register_mode": "1",
        "wlan_user_ip": get_ip(),
    }
    response = requests.get(url, params=payload)
    logger.debug(response)
    logger.debug(decode_unicode(response.text))
    response_text = decode_unicode(response.text)
    msg = parse_msg(response_text)
    res = int(msg["result"]) == 1
    logger.debug("注销%s", "成功" if res else "失败")
    return res, msg


# 登录


def try_to_connect_net(email_flag=None):
    """
    尝试连接网络。
    :param email_flag: 0-发送信息，1-仅在断开连接时发送信息，其他情况下-默认不发送信息
    """
    res = {}
    logger.info("初始状态信息:")
    res["初始状态"] = get_overall()

    chg = {}
    res["改变"] = chg
    is_chg = False
    if not is_login():
        logger.info("当前状态未登录, 尝试登录:")
        is_chg = True
        login_res, login_msg = login(user, passwd, )
        chg["动作"] = "登录"
        chg["登录结果"] = login_res
        chg["登录信息"] = login_msg
        chg["登陆后状态"] = get_overall()
    else:
        chg = "无变动"

    res_str = json.dumps(res, sort_keys=True, indent=4, ensure_ascii=False)
    if email_flag == 0:
        email_logger.info(res_str)
    elif email_flag == 1 and is_chg:
        email_logger.info(res_str)
    return res


# main


def main():
    import sys, getopt
    argv = sys.argv[1:]
    help_msg = """-h --help 获取帮助
    -m --mail 设置是否发送邮件，no-不发送，auto-只在断开连接时发送，默认发送
    """
    if len(argv) > 0:
        try:
            opts, args = getopt.getopt(argv, "hm", ["help", "mail="])
        except getopt.GetoptError:
            print("输入错误，-h 或 --help 获取帮助")
            sys.exit(2)

        for opt, arg in opts:
            if opt in ["-h", "--help"]:
                print(help_msg)
            elif opt in ["-m", "--mail"]:
                if arg == "no":
                    logger.info("不发送邮件")
                    try_to_connect_net()
                elif arg == "auto":
                    logger.info("仅在 ip 发送变化时发送邮件")
                    try_to_connect_net(1)
                else:
                    print("请输入正确的参数")
                    print(help_msg)
    else:
        logger.info("发送邮件")
        try_to_connect_net(0)  # 发送邮件


# res = try_to_connect_net()
if __name__ == "__main__":
    # 每隔五分钟检查是否联网，如果没有联网则连接，不发送消息
    # 每天早上 6:00 定时检查，并发送邮件查看状态信息
    # 如果在断网了，并且自动连接了，必须发送邮件说明
    main()
