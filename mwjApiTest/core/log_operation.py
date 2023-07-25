# -*- coding: utf-8 -*-
'''
@Time : 2023/7/10 15:28
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : log_operation.py
'''
__author__ = "梦无矶小仔"

import os
import logging
from logging.handlers import TimedRotatingFileHandler, BaseRotatingHandler
import colorama
import colorlog

# 初始化 colorama 库
colorama.init()


class Logger:
    __instance = None
    # 往屏幕上输出
    screen_output = logging.StreamHandler()

    def __new__(cls, path=None, level='DEBUG', RotatingFileHandler: BaseRotatingHandler = None):
        '''
        单列模式
        :param path: 报告的路径
        :param level: 日志的等级常用,INFO,DEBUG,WARNING,ERROR
        :param RotatingFileHandler:
        '''

        if not cls.__instance:
            colorama.init()
            cls.__instance = super().__new__(cls)
            log = logging.getLogger("mwjApiTest")
            # 设置日志级别
            log.setLevel(level)
            cls.__instance.log = log

        if path:
            if not os.path.isdir(path):
                os.mkdir(path)
            if RotatingFileHandler and isinstance(RotatingFileHandler, BaseRotatingHandler):
                fh = RotatingFileHandler
            else:
                # # 往文件里写入#指定间隔时间自动生成文件的处理器
                fh = TimedRotatingFileHandler(os.path.join(path, 'mwjApiTest.log'), when='D', interval=1,
                                              backupCount=7, encoding='utf-8')

            fh.setLevel(level)
            cls.__instance.log.addHandler(fh)
            # 定义handler的输出格式
            formatter = logging.Formatter("%(levelname)-8s%(asctime)s%(name)s:%(filename)s:%(lineno)d %(message)s")
            fh.setFormatter(formatter)
        return cls.__instance

    def set_level(self, level):
        """设置日志输出的等级"""
        self.log.setLevel(level)

    #### 设置输出的颜色
    def fontColor(self):
        # 不同的日志输出不同的颜色
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        )
        self.screen_output.setFormatter(formatter)
        self.log.addHandler(self.screen_output)

    def debug(self, message):
        self.fontColor()
        self.log.debug(message)

    def info(self, message):
        self.fontColor()
        self.log.info(message)

    def warning(self, message):
        self.fontColor()
        self.log.warning(message)

    def error(self, message):
        self.fontColor()
        self.log.error(message)

    def critical(self, message):
        self.fontColor()
        self.log.critical(message)


# 设置控制台输出颜色,兼容跨平台输出
def print_info(msg: str):
    print(colorama.Fore.GREEN + str(msg) + colorama.Style.RESET_ALL)


def print_waring(msg: str):
    print(colorama.Fore.YELLOW + str(msg) + colorama.Style.RESET_ALL)


def print_error(msg):
    print(colorama.Fore.RED + str(msg) + colorama.Style.RESET_ALL)

