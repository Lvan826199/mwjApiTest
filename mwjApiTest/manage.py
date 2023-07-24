# -*- coding: utf-8 -*-
'''
@Time : 2023/5/31 16:45
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : manage.py
'''
__author__ = "梦无矶小仔"

import argparse
import os
import unittest
from shutil import copytree

import mwjApiTest
from mwjApiTest.core.log_operation import print_info
from mwjApiTest.core.env_prepare import settings, log, ENV
from mwjApiTest.core.testRunner import TestRunner
from mwjApiTest.core.generateCase import ParserDataToCase


def create(args):
    '''创建项目'''
    if hasattr(args, "name"):
        name = args.name
        template_path = os.path.join(os.path.dirname(os.path.abspath(mwjApiTest.__file__)), 'templates')
        api_templates = os.path.join(template_path, 'request_file_demo')
        print_info("正在创建接口自动化项目:{}".format(name))
        try:
            copytree(api_templates, os.path.join('.', name))
        except Exception as e:
            print_info("项目创建失败！:{}".format(e))
        else:
            print_info("项目创建成功！")


def run(args=None):
    '''测试执行'''
    log.info('开始执行测试，加载用例....')
    if isinstance(args, argparse.Namespace):
        args = args
    else:
        if args is None:
            args = create_parser().parse_args(['run'])
        elif args[0] != 'run':
            args = create_parser().parse_args(['run'] + args)
        else:
            args = create_parser().parse_args(args)

    if hasattr(args, "file"):
        dir = os.path.abspath(getattr(args, 'file'))
    else:
        dir = os.path.abspath('.')

    # 判断路径是否是一个文件
    if os.path.isfile(dir):
        if dir.endswith('.yaml'):
            suite = ParserDataToCase.parser_yaml_create_cases(dir)
        elif dir.endswith('.json'):
            suite = ParserDataToCase.parser_json_create_cases(dir)
        elif dir.endswith('.py'):
            suite = unittest.defaultTestLoader.discover(os.path.dirname(dir), pattern=os.path.split(dir)[1])
        else:
            suite = unittest.TestSuite()

    elif os.path.isdir(dir):
        # load TestCase
        # load yaml TestCase
        yaml_dir = os.path.join(dir, 'case_yaml')
        suite1 = ParserDataToCase.parser_yaml_create_cases(yaml_dir)
        # load json TestCase
        json_dir = os.path.join(dir, 'case_json')
        suite2 = ParserDataToCase.parser_json_create_cases(json_dir)
        # load py TestCase
        case_dir = os.path.join(dir, 'case_py')
        suite3 = unittest.defaultTestLoader.discover(case_dir)
        suite = unittest.TestSuite()
        suite.addTest(suite1)
        suite.addTest(suite2)
        suite.addTest(suite3)
    else:
        suite = unittest.TestSuite()

    if suite == unittest.TestSuite():
        log.error('未加载到用例,请确认指定的用例路径或者目录是否正确！')
        log.error('执行路径为：{}'.format(dir))
        return
    # Test Result
    result = getattr(settings, 'TEST_RESULT', {})
    report_name = result.get('filename') if result.get('filename') else 'report.html'
    result['filename'] = report_name

    runner = TestRunner(suite=suite, **result)
    res = runner.run(thread_count=getattr(args, "thread") or getattr(settings, 'THREAD', 1),
                     rerun=getattr(args, "rerun") or getattr(settings, 'RERUN', 0),
                     interval=getattr(args, "interval") or getattr(settings, 'INTERVAL', 2)
                     )

    if hasattr(settings,'EMAIL'):
        try:
            # 邮件通知处理配置
            for k,v in getattr(settings,'EMAIL').items():
                if not v:
                    raise ValueError("邮件参数配置有误，setting.py文件中的EMAIL 的 {} 字段不能为空".format(k))
            else:
                runner.send_email(**getattr(settings,'EMAIL'))
        except Exception as e:
            log.error("测试结果邮件推送失败：{}".format(e))
        else:
            log.info("测试结果已发送到邮箱")

    if hasattr(settings, 'DINGTALK'):
        try:
            res = runner.dingtalk_notice(**settings.DINGTALK)
        except Exception as e:
            log.error("发送钉钉通知出错了，错误信息如下:{}".format(e))

        else:
            if res["errcode"] == 0:
                log.info("测试结果推送到钉钉群成功！")
            else:
                log.error("测试结果推送到钉钉群失败！错误信息:  {}".format(res["errmsg"]))

    if hasattr(settings, 'WECHAT'):
        try:
            res = runner.EnterpriseWeChat_notice(**settings.WECHAT)
        except Exception as e:
            log.error("测试结果推送到企业微信出错了，错误信息如下:  {}".format(e))
        else:
            if res["errcode"] == 0:
                log.info("测试结果推送到企业微信成功！")
            else:
                log.error("测试结果推送到企业微信失败！错误信息： {}".format(res["errmsg"]))
    return res

def create_parser():
    parser = argparse.ArgumentParser(prog='mwjApiTest', description='梦无矶接口测试框架使用介绍')
    # 添加版本号
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.1.4')
    subparsers = parser.add_subparsers(title='Command', metavar="命令")
    # 创建项目命令
    create_cmd = subparsers.add_parser('create', help=" 创建测试项目 ", aliases=['C'])
    create_cmd.add_argument('name', metavar='project_name', help=" 项目名称 ")
    create_cmd.set_defaults(func=create)
    # 运行项目命令
    parser_run = subparsers.add_parser('run', help=' 开始运行项目 ', aliases=['R'])
    parser_run.add_argument('--file', type=str, metavar='file', help='用例文件路径', default='.')
    parser_run.add_argument('--thread', type=int, metavar='thread', help='运行的并发线程数', default=None)
    parser_run.add_argument('--rerun', type=int, metavar='rerun', help='失败重跑的次数', default=None)
    parser_run.add_argument('--interval', type=int, metavar='interval', help='失败重跑的时间间隔', default=None)
    parser_run.set_defaults(func=run)
    ## 一定要return
    return parser


def main(params: list = None):
    """
    程序入口
    :param params: list
    :return:
    """
    parser = create_parser()
    # 获取参数
    if params:
        args = parser.parse_args(params)
    else:
        args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
