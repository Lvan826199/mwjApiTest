# -*- coding: utf-8 -*-
'''
@Time : 2023/5/31 16:55
@Email : Lvan826199@163.com
@公众号 : 梦无矶的测试开发之路
@File : setup.py.py
'''
__author__ = "梦无矶小仔"

import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mwj-apitest",  # 用自己的名替换其中的YOUR_USERNAME_
    version="1.0.0",  # 包版本号，便于维护版本,保证每次发布都是版本都是唯一的
    author="梦无矶小仔",  # 作者，可以写自己的姓名
    author_email="Lvan826199@163.com",  # 作者联系方式，可写自己的邮箱地址
    description="A small example package",  # 包的简述
    long_description=long_description,  # 包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/Lvan826199/mwjApiTest",  # 自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts" : ['mwjApiTest = mwjApiTest.manage:run']
    }, #安装成功后，在命令行输入mwjApiTest 就相当于执行了mwjApiTest.manage.py中的run了
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  # 对python的最低版本要求
)

