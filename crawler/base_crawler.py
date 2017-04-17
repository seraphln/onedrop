# coding=utf8
#


"""
爬虫的基本框架
"""

from gevent import monkey
monkey.patch_all()

import os
import sys
import json
import base64
import socket
import gevent
from gevent.queue import Queue
from gevent.pool import Group

import time
import signal

import requests

from crawler.api_proxy import register_crawler_node


class BaseCrawler(object):
    """ 基础的爬虫对象, 所有的爬虫都要继承自该对象 """

    WORKERS = {}

    def __init__(self, callback=None, ttype=None, source=None):
        """ 初始化爬虫对象 """
        self.group = Group()
        self.task_queue = Queue()
        self.task_type = ttype
        self.cb = callback
        self.source = source
        self.task_name = "%s-%s-%s" % (socket.gethostname(),
                                       self.source,
                                       self.task_type)

    def register(self):
        """ 将当前爬虫实例注册到服务器上 """
        task_result = {"name": self.task_name}
        bstr = base64.urlsafe_b64encode(json.dumps(task_result))
        resp = register_crawler_node(bstr)
        resp_name = resp.get("data", {}).get("cnodes", {}).get("cnode", {}).get("name")
        if resp_name != self.task_name:
            return False

        return True

    def get_task(self):
        """ 从远程接口获取需要采集的任务信息 """
        pass

    def process_worker(self):
        """
            任务执行主流程
            1. 注册爬虫
            2. 获取爬虫任务
            3. 处理任务
        """
        if not self.register():
            print "Register current node failed. Going Home Now!!!"
            return

        while True:
            task = None
            try:
                task = self.get_task()
            except Exception as e:
                print str(e)
                task = None
                if not task:
                    continue
            try:
                if self.cb:
                    if not self.cb(task):
                        print "No tasks, Going home now!!!, Bye!"
                        break
            except Exception as e:
                print 'task callback error:%s' % (e) 

    def start(self):
        self.group.spawn(self.process_worker)

    def kill_workers(self, pids, sig=signal.SIGQUIT):
        """
            杀掉当前的进程
        
            @param pids: 需要杀掉的进程列表
            @type pids: List

            @param sig: kill对应的信号
            @type sig: Signal
        """
        map(lambda pid: self.kill_worker(pid, sig), pids)

    def kill_worker(self, pid, sig=signal.SIGQUIT):
        """
            具体杀掉当前进程的方法

            @param pid: 需要kill掉的进程号
            @type pid: Int

            @param sig: kill对应的信号
            @type sig: Signal
        """
        try:
            os.kill(pid, sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                try:
                    worker = self.WORKERS.pop(pid)
                    #TODO: clean worker
                except (KeyError, OSError):
                    return
                else:
                    raise e


class BaseSeleniumCrawler(BaseCrawler):
    """
        使用selenium作为采集工具的基类
        所有使用selenium进行采集的插件都需要继承自该类
    """

    def __init__(self, callback, ttype=None, source=None):
        """ 初始化爬虫对象 """
        self.task_type = ttype
        self.source = source
        self.cb = callback
        self.task_name = "%s-%s-%s-%s" % ("selenium",
                                          socket.gethostname(),
                                          self.source,
                                          self.task_type)

    def process_worker(self):
        """
            任务执行主流程
            1. 注册爬虫
            2. 获取爬虫任务
            3. 处理任务
            4. 回传采集结果
        """
        if not self.register():
            print "Register current node failed. Going Home Now!!!"
            return

        while True:
            task = None
            try:
                task = self.get_task()
            except Exception as e:
                print str(e)
                task = None
                if not task:
                    continue
            try:
                if self.cb:
                    if not self.cb(task):
                        print "No tasks, Going home now!!!, Bye!"
                        break
            except Exception as e:
                print 'task callback error:%s' % (e) 

    def start(self):
        """ 启动任务 """
        self.process_worker()
