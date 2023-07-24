# -*- coding: utf-8 -*-
'''
@Time : 2023/7/10 15:25
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : env_prepare.py
'''
__author__ = "梦无矶小仔"

import importlib
import os, sys
from mwjApiTest.core.log_operation import Logger
from mwjApiTest.core.db_client import DBClient

# 把当前的根目录加进去路径集合里面
sys.path.append(os.getcwd())
sys.path.append(os.path.abspath('..'))  # 把项目根目录加进去
try:
    make_data_tools = importlib.import_module('funcTools')
except ModuleNotFoundError:
    from mwjApiTest.core import make_data as make_data_tools


class Settings:
    LOG_FILE_PATH = None
    DEBUG = True
    DB = []
    ENV = {}
    THREAD_COUNT = 1

try:
    settings = importlib.import_module('settings')
except:
    settings = Settings

if settings.DEBUG:
    log = Logger(path=getattr(settings, 'LOG_FILE_PATH', None),
                 level='DEBUG')
else:
    log = Logger(path=getattr(settings, 'LOG_FILE_PATH', None),
                 level='INFO')


class BaseEnv(dict):

    def __init__(self, name, **kwargs):
        self.__name = name
        print()
        super().__init__(**kwargs)

    def __setitem__(self, key, value):
        if self.__name == 'ENV':
            log.debug('设置全局变量:\n{:<10}: {}'.format(key, value))
        else:
            log.debug('设置局部变量:\n{:<10}: {}'.format(key, value))
        super().__setitem__(key, value)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        # 由于我们用的是self.__name私有变量，正常如果使用 self.name 的话，key就是name
        # 现在用了私有变量，我们的name就会被python处理，变成_BaseEnv__name，所以key是_BaseEnv__name
        # 而 value就是我们初始化init传进来的name
        if key != '__name' and key != '_BaseEnv__name':
            self.__setitem__(key, value)

    def __getattr__(self, item):
        if item != '__name' and item != '_BaseEnv__name':
            return super().__getitem__(item)
        return super().__getattribute__(item)

    def __delattr__(self, item):
        if item != '__name' and item != '_BaseEnv__name':
            super().__delitem__(item)
        else:
            super().__delattr__()


ENV = BaseEnv('ENV')
ENV.update(getattr(settings, 'ENV', {}))  # 更新 "ENV", 如果没有，则 "ENV" = {}
DB = DBClient(getattr(settings, 'DB', []))  # 获取 'DB', 如果没有，则 'DB' = {}
