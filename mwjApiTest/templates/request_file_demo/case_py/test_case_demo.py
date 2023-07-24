# -*- coding: utf-8 -*-
'''
@Time : 2023/7/21 14:02
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : test_case_demo.py.py
'''
__author__ = "梦无矶小仔"
from mwjApiTest.core.httptest import HttpCase


class TestDome1(HttpCase):
    # host地址,如果setting中定义了此处可以不写
    host = "http://httpbin.org"
    # 请求头
    headers = {
        "UserAgent": "python/mwjapitest"
    }
    # 请求方法
    method = 'get'
    # 接口地址
    interface = '/get'
    # 指定用例级别的前置钩子
    setup_hook = "setup_hook_demo"
    # 指定用例级别的猴子猴子
    teardown_hook = "teardown_hook_demo"
    # 用例断言
    verification = [
        ["eq", 200, "status_code"]
    ]
    # 用例数据
    Cases = [
        # 用例1
        {
            "title": "py文件-用例1",
            "json": {
                "mobile_phone": "18812345678",
                "pwd": "xiaozai"
            },
        },
        # 用例2
        {
            "title": "py文件-用例2",
            "json": {
                "mobile_phone": "17796325874",
                "pwd": "xiaozai"
            }
        }
    ]
