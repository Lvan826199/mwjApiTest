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


class Logger:
    __instance = None
    sh = logging.StreamHandler()

    def __new__(cls, path=None, level='DEBUG', RotatingFileHandler: BaseRotatingHandler = None):
        '''
        单列模式
        :param path: 报告的路径
        :param level: 日志的等级常用,INFO,DEBUG,WARNING,ERROR
        :param RotatingFileHandler:
        '''

        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            log = logging.getLogger("mwjApiTest")
            log.setLevel(level)
            cls.__instance.log = log

        if path:
            if not os.path.isdir(path):
                os.mkdir(path)
            if RotatingFileHandler and isinstance(RotatingFileHandler, BaseRotatingHandler):
                fh = RotatingFileHandler
            else:
                fh = TimedRotatingFileHandler(os.path.join(path, 'mwjApiTest.log'), when='D', interval=1,
                                              backupCount=7, encoding='utf-8')

            fh.setLevel(level)
            cls.__instance.log.addHandler(fh)
            # 定义handler的输出格式
            formatter = logging.Formatter("%(asctime)s | 【%(levelname)s】 | : %(message)s")
            fh.setFormatter(formatter)
        return cls.__instance

    def set_level(self, level):
        """设置日志输出的等级"""
        self.log.setLevel(level)

    def set_file_handle(self, level, path):
        if path:
            if not os.path.isdir(path):
                os.mkdir(path)
            fh = TimedRotatingFileHandler(os.path.join(path, 'mwjApiTest.log'), when='D',
                                          interval=1, backupCount=7,
                                          encoding="utf-8")
            fh.setLevel(level)
            self.log.addHandler(fh)
            # 定义handler的输出格式
            formatter = logging.Formatter("%(asctime)s | 【%(levelname)s】 | : %(message)s")
            fh.setFormatter(formatter)

    #### 设置输出的颜色
    def fontColor(self, color):
        # 不同的日志输出不同的颜色
        formatter = logging.Formatter(color.format("%(asctime)s| ", "【%(levelname)s】", " | : %(message)s"))
        self.sh.setFormatter(formatter)
        self.log.addHandler(self.sh)

    def debug(self, message):
        self.fontColor('\033[0;34m{}\033[0;34m{}\033[0;34m{}')
        self.log.debug(message)

    def info(self, message):
        self.fontColor('\033[0;32m{}\033[0;32m{}\033[0;32m{}')
        self.log.info(message)

    def warning(self, message):
        self.fontColor('\033[0;33m{}\033[0;43m{}\033[0;33m{}')
        self.log.warning(message)

    def error(self, message):
        self.fontColor('\033[0;31m{}\033[0;41m{}\033[0;31m{}')
        self.log.error(message)

    def exception(self, message):
        self.fontColor('\033[0;31m{}\033[0;41m{}\033[0;31m{}')
        self.log.exception(message)

    def critical(self, message):
        self.fontColor('\033[0;35m{}\033[0;45m{}\033[0;35m{}')
        self.log.critical(message)


# 设置控制台输出颜色
def print_info(msg):
    print('\033[0;32m{}'.format(msg))


def print_waring(msg):
    print('\033[0;33m{}'.format(msg))


def print_error(msg):
    print('\033[0;31m{}'.format(msg))
