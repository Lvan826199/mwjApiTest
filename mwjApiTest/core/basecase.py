# -*- coding: utf-8 -*-
'''
@Time : 2023/7/12 17:37
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : basecase.py
'''
__author__ = "梦无矶小仔"

import datetime
import os
import yaml
import json
import unittest
from functools import wraps
from mwjApiTest.core.dataParser import DataParser
from mwjApiTest.core.env_prepare import BaseEnv, log, settings


class CaseLog:
    log = log

    def save_log(self, message, level):
        if not hasattr(self, 'log_data'):
            setattr(self, 'log_data', [])  # 给对象 self 添加一个名为 log_data 的属性，并将其初始化为一个空列表。
        info = "【{}】| {} |: {}".format(level, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), message)
        getattr(self, 'log_data').append((level, info))

    def save_error(self, message):
        if not hasattr(self, 'error_info'):
            setattr(self, 'error_info', [])
        getattr(self, 'error_info').append("【ERROR】:{} ".format(message))

    def debug_log(self, message):
        if settings.DEBUG:
            self.save_log(message, 'DEBUG')
            self.log.debug(message)

    def info_log(self, message):
        self.save_log(message, 'INFO')
        self.log.info(message)

    def warning_log(self, message):
        self.save_log(message, 'WARNING')
        self.log.warning(message)

    def error_log(self, message):
        self.save_log(message, 'ERROR')
        self.save_error(message)
        self.log.error(message)

    def exception_log(self, message):
        self.save_log(message, 'ERROR')
        self.save_error(message)
        self.log.exception(message)

    def critical_log(self, message):
        self.save_log(message, 'CRITICAL')
        self.save_error(message)
        self.log.critical(message)


class GenerateTest(type):
    """生成用例的类"""

    def __new__(cls, name, bases, namespace, *args, **kwargs):
        if name in ('BaseTestCase', 'HttpCase'):
            return super().__new__(cls, name, bases, namespace)
        else:
            # -------------------生成用例---------------------
            # Case外的类属性中，是否有需要动态执行的函数
            # 遍历字典，强转为列表，键值对会转化为元组
            # 示例 {"Cases":[1,3,4],"headers":"hello"} --> [('Cases', [1, 2, 3, 4]), ('headers', 'hello')]
            for key, value in list(namespace.items()):
                if key not in ['Cases', "extract", "verification", 'headers']:
                    # 解析数据中的变量
                    value = DataParser.parser_func(namespace.get('env'), value)
                    value = DataParser.parser_variable(namespace.get('env'), value)
                    namespace[key] = value

                if key == 'env':
                    _value = BaseEnv('env')
                    _value.update(value)

            test_cls = super().__new__(cls, name, bases, namespace)
            func = getattr(test_cls, "perform")
            datas = cls.__handle_datas(namespace.get("Cases"))

            for index, case_data in enumerate(datas):
                # 生成用例名称
                new_test_name = cls.__create_test_name(index, case_data, test_cls)
                # 生成用例描述
                if isinstance(case_data, dict) and case_data.get("title"):
                    test_desc = case_data.get("title")
                elif isinstance(case_data, dict) and case_data.get("desc"):
                    test_desc = case_data.get("desc")
                elif hasattr(case_data, 'title'):
                    test_desc = case_data.title
                else:
                    test_desc = func.__doc__
                # 对变量进行处理，从而传递给测试方法
                func2 = cls.__update_func(new_test_name, case_data, test_desc, func)
                setattr(test_cls, new_test_name, func2)
            return test_cls

    @classmethod
    def __update_func(cls, new_func_name, params, test_desc, func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, params, *args, **kwargs)

        wrapper.__wrapped__ = func
        wrapper.__name__ = new_func_name
        wrapper.__doc__ = test_desc
        return wrapper

    @classmethod
    def __create_test_name(cls, index, case_data, test_cls):
        interface = case_data.get('interface') or getattr(test_cls, 'interface')
        if index + 1 < 10:
            test_name = 'test' + "_0" + str(index + 1) + '_' + interface.strip('/').replace('/', '_')
        else:
            test_name = 'test' + "_" + str(index + 1) + '_' + interface.strip('/').replace('/', '_')
        return test_name

    @classmethod
    def __handle_datas(cls, datas):
        if isinstance(datas, list):
            return datas

        if isinstance(datas, str) and datas.endswith('.json') or datas.endswith('.yaml'):
            if os.getcwd().split() == "case_py":
                filepath = os.path.join("..", "case_yaml", datas)
            else:
                filepath = os.path.join(".", 'case_yaml', datas)

            # 支持json
            if filepath.endswith('.json'):
                with open(filepath, 'rb') as f:
                    return json.load(f)
            # 支持yaml
            if filepath.endswith('.yaml'):
                with open(filepath, 'rd') as f:
                    return yaml.load(f, Loader=yaml.FullLoader)

            # 其他格式暂不支持,后续待开发excel

        raise ValueError("测试用例数据格式错误,请检查！")


class BaseTestCase(unittest.TestCase, CaseLog, metaclass=GenerateTest):
    name = ''

    def perform(self, item):
        pass

    def get(self, attr):
        """支持通过get方法获取属性"""
        return getattr(self, attr, None)
