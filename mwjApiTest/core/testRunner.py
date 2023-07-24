# -*- coding: utf-8 -*-
'''
@Time : 2023/7/10 18:03
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : testRunner.py
'''
__author__ = "梦无矶小仔"

import os
import copy
import re
import unittest
import time
import json

from jinja2 import Environment, FileSystemLoader
from concurrent.futures.thread import ThreadPoolExecutor

from mwjApiTest.core.env_prepare import log
from mwjApiTest.core.send_report import SendEmail, DingTalk, EnterpriseWeChat


class TestResult(unittest.TestResult):
    '''测试结果记录'''

    def __init__(self):
        super().__init__()
        self.fields = {
            "success": 0,
            "all": 0,
            "fail": 0,
            "skip": 0,
            "error": 0,
            "begin_time": "",
            "results": [],
            "testClass": '',
            "res": ""
        }

    def startTest(self, test):
        '''
        当测试用例测试即将运行时调用(unittest.result自带的方法)
        :param test:
        :return:
        '''
        super().startTest(test)
        self.start_time = time.time()
        getattr(test, 'info_log')("开始执行用例：【{}】\n".format(test._testMethodDoc or test))

    def stopTest(self, test):
        """
        当测试用列执行完成后进行调用
        :return:
        """
        super().stopTest(test)
        # 获取用例的执行时间
        test.run_time = '{:.3}s'.format((time.time() - self.start_time))
        test.class_name = test.__class__.__qualname__
        test.method_name = test.__dict__['_testMethodName']
        test.method_doc = test.shortDescription()
        self.fields['results'].append(test)
        # 获取测试类名和描述信息
        self.fields["testClass"] = getattr(test, 'name')

    def stopTestRun(self, title=None) -> None:
        """
        测试用例执行完手动调用统计测试结果的相关数据
        :param title:
        :return:
        """
        self.fields['fail'] = len(self.failures)
        self.fields['error'] = len(self.errors)
        self.fields['skip'] = len(self.skipped)
        self.fields['all'] = sum(
            [self.fields['fail'], self.fields['error'], self.fields['skip'], self.fields['success']])

        if len(self.errors) > 0:
            self.fields['res'] = 'error'

        elif len(self.failures) > 0:
            self.fields['res'] = 'fail'
        else:
            self.fields['res'] = 'success'

    def addSuccess(self, test):
        """用例执行通过，成功数量+1"""
        self.fields["success"] += 1
        test.state = '成功'
        getattr(test, 'info_log')("{}执行——>【通过】\n".format(test._testMethodDoc))
        test.run_info = getattr(test, 'base_info', None)

    def addFailure(self, test, err):
        """
        :param test: 测试用例
        :param err:  错误信息
        :return:
        """
        super().addFailure(test, err)
        test.state = '失败'
        # 保存错误信息
        getattr(test, 'warning_log')(err[1])
        getattr(test, 'warning_log')("{}执行——>【失败】\n".format(test._testMethodDoc))
        test.run_info = getattr(test, 'base_info', None)

    def addSkip(self, test, reason):
        """
        修改跳过用例的状态
        :param test:测试用例
        :param reason: 相关信息
        :return: None
        """
        super().addSkip(test, reason)
        test.state = '跳过'
        getattr(test, 'info_log')("{}执行--【跳过Skip】\n".format(test._testMethodDoc))
        test.run_info = reason

    def addError(self, test, err):
        """
        修改错误用例的状态
        :param test: 测试用例
        :param err:错误信息
        :return:
        """
        super().addError(test, err)
        test.state = '错误'
        getattr(test, 'error_log')(err[1])
        getattr(test, 'error_log')("{}执行——>【错误Error】\n".format(test._testMethodDoc))
        if test.__class__.__qualname__ == '_ErrorHolder':
            test.run_time = 0
            res = re.search(r'(.*)\(.*\.(.*)\)', getattr(test, 'description'))
            test.class_name = res.group(2)
            test.method_name = res.group(1)
            test.method_doc = test.shortDescription()
            self.fields['results'].append(test)
            self.fields["testClass"] = test.class_name
        test.run_info = getattr(test, 'base_info', None)


class ReRunResult(TestResult):
    """重运行机制"""

    def __init__(self, count, interval):
        super().__init__()
        self.count = count
        self.interval = interval
        self.run_cases = []

    def startTest(self, test):
        if not hasattr(test, "count"):
            super().startTest(test)

    def stopTest(self, test):
        if test not in self.run_cases:
            self.run_cases.append(test)
            super().stopTest(test)

    def addFailure(self, test, err):
        """
        :param test: 测试用例
        :param err:  错误信息
        :return:
        """
        if not hasattr(test, 'count'):
            test.count = 0
        if test.count < self.count:
            test.count += 1
            getattr(test, 'warning_log')("{}执行——>【失败Failure】\n".format(test))
            getattr(test, 'warning_log')(err[1])
            getattr(test, 'warning_log')("开始第{}次重运行\n".format(test.count))
            time.sleep(self.interval)
            test.run(self)
        else:
            super().addFailure(test, err)
            if test.count != 0:
                getattr(test, 'warning_log')("重运行{}次完毕\n".format(test.count))

    def addError(self, test, err):
        """
        修改错误用例的状态
        :param test: 测试用例
        :param err:错误信息
        :return:
        """
        if not hasattr(test, 'count'):
            test.count = 0
        if test.count < self.count:
            test.count += 1
            getattr(test, 'error_log')("{}执行——>【错误Error】\n".format(test))
            getattr(test, 'exception_log')(err[1])
            getattr(test, 'error_log')("================{}重运行第{}次================\n".format(test, test.count))
            time.sleep(self.interval)
            test.run(self)
        else:
            super().addError(test, err)
            if test.count != 0:
                getattr(test, 'info_log')("================重运行{}次完毕================\n".format(test.count))


class TestRunner():
    """unittest运行程序"""

    def __init__(self, suite: unittest.TestSuite,
                 filename="reports.html",
                 report_dir="./reports",
                 title='接口测试报告',
                 tester='测试员-梦无矶',
                 desc="公司接口项目测试生成的报告",
                 templates=2,
                 no_report=False
                 ):
        '''
        初始化用例运行程序
        :param suite:测试套件
        :param filename:测试报告的文件名
        :param report_dir:测试报告的存放路径
        :param title:测试套件的标题
        :param tester:测试人员
        :param desc:测试报告的描述
        :param templates:可以通过参数值1或2，指定报告的样式模板，目前有两个模板
        :param no_report:不生成测试报告，以json数据格式返回测试结果，默认生成，设置True则不生成报告
        '''
        if not isinstance(suite, unittest.TestSuite):
            raise TypeError("suites 不是测试套件 请检查类型")
        if not isinstance(filename, str):
            raise TypeError("filename is not str")
        if not filename.endswith(".html"):
            filename = filename + ".html"

        self.suite = suite
        self.filename = filename
        self.report_dir = report_dir
        self.title = title
        self.tester = tester
        self.desc = desc
        self.templates = templates
        self.no_report = no_report
        self.start_time_test = time.time()
        self.result = []

    def __classification_suite(self):
        '''
        分类规则
        将测试套件中的用例，根据用例类位单位，拆分成多个测试套件，打包成列表类型
        :return: list-->[suite,suite,suite.....]
        '''

        suites_list = []

        def wrapper(suite):
            for item in suite:
                if isinstance(item, unittest.TestCase):
                    suites_list.append(suite)
                    break
                else:
                    wrapper(item)

        wrapper(copy.deepcopy(self.suite))
        return suites_list

    def __get_results(self, test_result):
        '''

        :param test_result:传入self.test_result 整合的测试结果汇总
        :return: 返回测试结果
        '''
        results = []
        for cls in test_result.get('results'):
            # 将对象转换为dict类型
            cls['casesRes'] = [{k: v for k, v in case.__dict__.items() if not k.startswith('_')} for case in cls['casesRes']]
            results.append(cls)
        test_result['results'] = results
        return test_result

    def __get_notice_content(self):
        '''
        获取通知的内容，使用模板语言进行处理
        可以根据字段在模板中进行增删
        :return: 返回文本格式
        '''
        template_path = os.path.join(os.path.dirname(__file__), '../templates/reports')
        env = Environment(loader=FileSystemLoader(template_path))
        res_text = env.get_template("dingtalk_templates.md").render(self.test_result)
        return res_text

    def __handle_history_data(self, test_result):
        '''
        处理历史数据
        :param test_result: 测试结果汇总
        :return: history_data 历史数据
        '''
        try:
            with open(os.path.join(self.report_dir, 'history.json'), 'r', encoding='utf-8') as f:
                history = json.load(f)
        except FileNotFoundError as e:
            history = []

        history.append(
            {'success': test_result['success'],
             'all': test_result['all'],
             'fail': test_result['fail'],
             'skip': test_result['skip'],
             'error': test_result['error'],
             'runtime': test_result['runtime'],
             'begin_time': test_result['begin_time'],
             'pass_rate': test_result['pass_rate'],
             }
        )

        with open(os.path.join(self.report_dir, 'history.json'), 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=True)

        return history

    def __get_reports(self, thread_count):
        '''
        生成报告,返回测试汇中的结果
        :param thread_count: 线程数量，默认位1
        :return: 包含测试结果的字典
        '''
        # 汇总测试结果
        test_result = {
            "success": 0,
            "all": 0,
            "fail": 0,
            "skip": 0,
            "error": 0,
            "results": [],
            "classNames": [],

        }

        # 整合测试结果
        for res in self.result:
            test_result["success"] += res.fields["success"]
            test_result["all"] += res.fields["all"]
            test_result["fail"] += res.fields["fail"]
            test_result["error"] += res.fields["error"]
            test_result["skip"] += res.fields["skip"]
            test_result["results"].append({
                'name': res.fields["testClass"],
                'casesRes': res.fields["results"],
                "res": res.fields["res"],
                'fail': res.fields["fail"],
                'error': res.fields["error"],
                'success': res.fields["success"]
            })
            test_result["classNames"].append(res.fields["testClass"])

        test_result['thread_count'] = thread_count
        test_result['runtime'] = '{:.2f} S'.format(time.time() - self.start_time_test)
        test_result["begin_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time_test))
        test_result["title"] = self.title
        test_result["tester"] = self.tester
        test_result['desc'] = self.desc
        if test_result['all'] != 0:
            test_result['pass_rate'] = '{:.2f}'.format(test_result['success'] / test_result['all'] * 100)
        else:
            test_result['pass_rate'] = 0

        log.info("用例运行完毕,结果如下：\n共运行：{}条 "
                 "\n通过:{}条"
                 "\n失败:{}条"
                 "\n错误:{}条"
                 "\n运行时间:{}".format(
            test_result['all'], test_result['success'], test_result['fail'], test_result['error'],
            test_result['runtime']
        ))

        self.test_result = test_result
        # 判断是否要生产测试报告
        if os.path.isdir(self.report_dir):
            pass
        else:
            os.mkdir(self.report_dir)

        if self.no_report:
            return self.__get_results(test_result)

        log.info("正在为您生成测试报告,请稍等...")

        # 获取历史执行数据
        test_result['history'] = self.__handle_history_data(test_result)
        # 获取报告模板
        template_path = os.path.join(os.path.dirname(__file__), '../templates/reports')
        env = Environment(loader=FileSystemLoader(template_path))
        if self.templates == 2:
            template = env.get_template('templates2.html')
        else:
            template = env.get_template('templates1.html')

        file_path = os.path.join(self.report_dir, self.filename)

        # 渲染报告模板
        res = template.render(test_result)

        # 输出报告到文件
        with open(file_path, 'wb') as f:
            f.write(res.encode('utf-8'))

        # log_print_path = os.path.join(os.getcwd(),file_path)
        log.info("测试报告已经生成，报告路径为:{}".format(file_path))
        self.email_content = {
            "file": os.path.abspath(file_path),
            "content": env.get_template('templates03.html').render(test_result)
        }

        return {'success': test_result['success'],
                'all': test_result['all'],
                'fail': test_result['fail'],
                'skip': test_result['skip'],
                'error': test_result['error'],
                'runtime': test_result['runtime'],
                'begin_time': test_result['begin_time'],
                'tester': test_result['tester'],
                'pass_rate': test_result['pass_rate'],
                'report': file_path,
                "thread_count": thread_count
                }

    def run(self, thread_count=1, rerun=0, interval=2):
        '''
        支持多线程执行
        注意点：如果多个测试类共用某一个全局变量，由于资源竞争可能会出现错误
        :param thread_count: 线程数量，默认位1
        :param rerun: 重运行次数
        :param interval:运行时间间隔,单位为秒
        :return: 测试运行结果
        '''

        # 将测试套件按照用例类进行拆分
        suites = self.__classification_suite()
        with ThreadPoolExecutor(max_workers=thread_count) as ts:
            for i in suites:
                res = ReRunResult(count=rerun, interval=interval)
                self.result.append(res)
                ts.submit(i.run, result=res).add_done_callback(res.stopTestRun)
            ts.shutdown(wait=True)
        result = self.__get_reports(thread_count)
        return result

    def get_except_info(self):
        '''获取运行错误用例和运行失败用例的报告信息'''
        except_info = []
        num = 0
        for i in self.result:
            for texts in i.failures:
                t, content = texts
                num += 1
                except_info.append("*{}、用例【{}】执行失败*，\n失败信息如下：".format(num, t._testMethodDoc))
                except_info.append(content)

            for texts in i.errors:
                num += 1
                t, content = texts
                except_info.append("*{}、用例【{}】执行错误*，\n错误信息如下：".format(num, t._testMethodDoc))
                except_info.append(content)

        except_str = "\n".join(except_info)
        return except_str

    def send_email(self, host: str, port: int, email_account: str, password: str, to_addrs, is_file=True):
        '''
        通过邮箱发送测试报告内容
        :param host: SMTP server address
        :param port: SMTP server port
        :param email_account: 邮箱
        :param password: 邮箱的smtp服务授权码
        :param to_addrs: 接收方的邮箱
        :param is_file: 判断是否发送文件
        :return:
        '''

        sm = SendEmail(host=host, port=port, email_account=email_account, password=password)
        if is_file:
            file_name = self.email_content['file']
        else:
            file_name = None
        content = self.email_content['content']

        sm.send_email(subject=self.title, content=content, filename=file_name, to_addrs=to_addrs)

    def dingtalk_notice(self, webhook, key=None, secret=None, atMobiles=None, isatall=False, except_info=False):
        '''

        :param webhook: 钉钉机器人的Webhook地址
        :param key: （非必传：str类型）如果钉钉机器人安全设置了关键字，则需要传入对应的关键字
        :param secret: （非必传:str类型）如果钉钉机器人安全设置了签名，则需要传入对应的密钥
        :param atMobiles: （非必传，list类型）发送通知钉钉中要@人的手机号列表，如：[137xxx,188xxx]
        :param isatall: 是否@所有人，默认为False,设为True则会@所有人
        :param except_info: 是否发送未通过用例的详细信息，默认为False，设为True则会发送失败用例的详细信息
        :return: 发送成功返回 {"errcode":0,"errmsg":"ok"}  发送失败返回 {"errcode":错误码,"errmsg":"失败原因"}
        '''
        res_text = self.__get_notice_content()
        if except_info:
            res_text += '\n ### 未通过用例详情： \n'
            res_text += self.get_except_info()

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": '{}({})'.format(self.title, key),
                "text": res_text
            },
            "at": {
                "atMobiles": atMobiles,
                "isAtAll": isatall
            }
        }

        ding = DingTalk(webhook=webhook, data=data, secret=secret)
        response = ding.send_info()
        return response.json()

    def EnterpriseWeChat_notice(self, chatid, access_token=None, corpid=None, corpsecret=None):
        '''
        测试结果推送到企业微信群，【access_token】和【corpid，corpsecret】至少要传一种
        可以传入access_token ,也可以传入（corpid，corpsecret）来代替access_token
        :param chatid: 企业微信群ID
        :param access_token: 调用企业微信API接口的凭证
        :param corpid: 企业ID
        :param corpsecret: 应用的凭证密钥
        :return:
        '''

        # 获取通知结果
        res_text = self.__get_notice_content()
        data = {
            "chatid": chatid,
            "msgtype": "markdown",
            "markdown": {
                "content": res_text
            }
        }
        weChat = EnterpriseWeChat(access_token=access_token, corpid=corpid, corpsecret=corpsecret)
        response = weChat.send_info(data=data)
        return response


