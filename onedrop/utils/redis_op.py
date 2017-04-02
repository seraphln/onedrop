# coding=utf8
#

"""
redis操作的封装
"""


from redis import Redis
from django.conf import settings


class RedisOp(object):
    """ 一个基础的针对redis操作的封装 """
    def __init__(self, host=settings.REDIS_HOST, port=settings.REDIS_PORT):
        self.host = host
        self.port = port
        self.redis_db = self.open_connection()

    def open_connection(self):
        """ 打开redis的链接 """
        return Redis(host=self.host, port=self.port)

    def get_task_queue_length(self, queue):
        """ 获取任务队列的长度 """
        return self.redis_db.llen(queue)

    def add_task_queue(self, queue, value):
        """ 向任务队列中写入任务 """
        return self.redis_db.rpush(queue, value)

    def get_task_from_queue(self, queue, timeout=1):
        """ 从队列中获取一个任务信息 """
        return self.redis_db.lpop(queue)


rop = RedisOp()
