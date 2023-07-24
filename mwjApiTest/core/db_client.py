# -*- coding: utf-8 -*-
'''
@Time : 2023/7/10 15:28
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : db_client.py
'''
__author__ = "梦无矶小仔"


class DBMysql:
    '''mysql数据库相关操作'''

    def __init__(self, config):
        import pymysql
        config['autocommit'] = True
        # 连接数据库
        self.connect = pymysql.connect(**config)
        # 建立游标，获取数据库数据为字典格式
        self.cursor = self.connect.cursor(pymysql.cursors.DictCursor)

    def execute(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def execute_all(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def __del__(self):
        self.cursor.close()
        self.connect.close()


class DBClient:

    def __init__(self, DB):
        for config in DB:
            if not config.get('name'): raise ValueError('数据库配置的name字段不能为空！')
            if config.get('db'):
                setattr(self, config.get('name'), config.get('db'))
            elif config.get('type').lower() == 'mysql' and config.get('config'):
                setattr(self, config.get('name'), DBMysql(config.get('config')))
            else:
                raise ValueError('您传入的数据库配置有误，或者mwjApiTest目前不支持此数据库：{}'.format(config))
