#!/usr/bin/env python
# coding: utf-8
import re
import json
import requests
from .project_config import *


def decode_unicode(s):
    """
    将 unicode 字符串解码
    """
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
    """
    解析请求结果
    """
    logger.debug("解析 msg: %s", msg)
    msg_json_text = re.search("\{.*\}", msg)
    res = json.loads(msg_json_text.group(0))
    return res


def get_status(ip=None):
    """
    状态
    从状态中可以知道对应 ip 对应的用户是谁，而注销只需要知道 ip 和用户。所以可以通过扫描所有 ip 的状态，注销任何指定用户或者指定 ip 。
    """
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
    """
    是否已经登录
    """
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


def login(user, passwd, is_keep=False, ip=None):
    """
    登录网关
    """
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
    }
    response = requests.get(url, params=payload)
    logger.debug(response)
    logger.debug(decode_unicode(response.text))
    response_text = decode_unicode(response.text)
    msg = parse_msg(response_text)
    res = int(msg["result"]) == 1
    logger.debug("登录%s", "成功" if res else "失败")
    return res, msg


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
