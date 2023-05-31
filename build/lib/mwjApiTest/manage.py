# -*- coding: utf-8 -*-
'''
@Time : 2023/5/31 16:45
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : manage.py
'''
__author__ = "梦无矶小仔"
import argparse
import mwjApiTest


def run():
    '''123测试上传'''
    print("测试run接口执行输出。。。")

def create_parser():
    parser = argparse.ArgumentParser(prog='mwjApiTest', description='接口命令使用介绍')
    # 添加版本号
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0.0')
