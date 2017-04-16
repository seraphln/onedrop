# coding=utf8
#


"""
数据库交互相关函数
从models文件中抽出来
"""

import json
import base64
from django.conf import settings
from django.utils import timezone

from onedrop.utils.redis_op import rop

from onedrop.odtasks.models import CrawlerNodes
from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks


def get_data_from_b64string(result):
    """
        将给定的urlsafe_64encode的字符串解析成原始格式
        如果出现异常，则返回空字典

        @param result: 给定的需要解码的字符串
        @type result: String

        :return: {}
    """
    try:
        data = json.loads(base64.urlsafe_b64decode(str(result)))
    except:
        data = {}

    return data


def update_cnodes(result, remote_addr):
    """
        注册爬虫信息
        @param result: 爬虫信息的base64编码的字符串
        @type result: String

        @param remote_addr: 从environ中取出的客户端的IP
        @type remote_addr: String

        :return: cnode
    """
    now = timezone.now()
    data = get_data_from_b64string(result)

    cnode, _ = CrawlerNodes.objects.get_or_create(name=data.get("name"),
                                                  remote_addr=remote_addr)
    cnode.last_join_on = now
    cnode.status = "active"
    cnode.name = cnode.name.encode('utf8')
    cnode.save()
    return cnode


def update_ctasks(result):
    """
        根据参数来更新对应的crawler_task实例

        @param result: 爬虫发回来的base64编码的信息
        @type result: String

        :return: crawler_task instance
    """
    now = timezone.now()
    data = get_data_from_b64string(result)

    url, name, category, ttype = (data.get("url"),
                                  data.get("name"),
                                  data.get("category"),
                                  data.get("ttype"))

    # 4个字段必须同时存在，如果不存在则认为本次请求有问题
    if any([not url, not name, not category, not ttype]):
        return None
    else:
        ct, flag = CrawlerTasks.objects.get_or_create(url=url,
                                                      ttype=ttype,
                                                      name=name,
                                                      category=category)
        source = data.ge("source")

        # 先判断当前的task和source是否存在，如果不存在，则返回
        queue = settings.TASK_QUEUE_MAPPER.get("task").get(source)
        if not queue:
            return None
        # 新创建的记录
        if flag:
            ct.created_on = now
            if "parent_category" in data:
                ct.parent_category = data.get("parent_category")

            # 更新任务来源
            ct.source = source
            # 将任务发送到消息队列
            rop.add_task_queue(queue, str(ct.id))
        # 更新记录
        else:
            # 如果没有content也没有page的话，认为本次抓取失败
            # 则需要把当前的采集任务再放回到任务队列中
            if not data.get("content") and not data.get("page"):
                # 修改任务状态
                ct.status = "pending"
                ct.save()
                rop.add_task_queue(queue, str(ct.id))
                # 任务加入到redis之后，直接退出
                return

            # 将传递过来的content, result, page
            ct.status = "finished"
            ct.content = data.get("content")
            ct.result = data.get("result")
            ct.page = data.get("page")
            ct.last_crawl_on = now

        ct.modified_on = now
        ct.save()
        ct.name = ct.name.encode('utf8')
        return ct


def get_crawler_task(ttype="task", source=None):
    """
        从任务队列获取一个采集任务

        @param ttype: 当前的任务类型
        @type ttype: String

        @param source: 任务来源类型
        @type source: String

        :return: [task_obj, ]
    """
    now = timezone.now()
    if ttype == "seed":
        queue = settings.TASK_QUEUE_MAPPER.get(ttype)
    else:
        queue = settings.TASK_QUEUE_MAPPER.get(ttype).get(source)

    tid = rop.get_task_from_queue(queue=ttype)
    if not tid:
        return []

    # 获取任务、更新任务状态返回任务实例
    tid = int(tid)
    if source == "seed":
        obj = CrawlerSeeds.objects.filter(id=tid).first()
    else:
        obj = CrawlerTasks.objects.filter(id=tid).first()

    obj.last_crawl_on = now
    obj.status = "running"
    obj.save()
    return [obj, ]
