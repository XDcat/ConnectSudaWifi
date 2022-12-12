# -*- coding:utf-8 -*-
import os
import logging.config

# 登录信息
# suda account information
user = "学号"
passwd = "密码"
# email information
mailhost = "邮箱服务器"
fromaddr = ""
toaddrs = ["接受邮件地址", ]
subject = "logger: 自动连接苏大网"
credentials = ("发送邮箱", "发送邮箱密码")  # 用户，密码
# log 控制台输出等级
level_log_console = "INFO"
log_file_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, "project.log")


# log 配置
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
            "filename": log_file_name,  # 必选, 文件名称
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
