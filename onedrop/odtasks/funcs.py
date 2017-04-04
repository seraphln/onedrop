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
from onedrop.odtasks.models import CrawlerTasks


def update_cnodes(result, remote_addr):
    """ 注册爬虫信息 """
    now = timezone.now()
    try:
        data = json.loads(base64.urlsafe_b64decode(str(result)))
    except:
        data = {}

    cnode, _ = CrawlerNodes.objects.get_or_create(name=data.get("name"),
                                                  remote_addr=remote_addr)
    cnode.last_join_on = now
    cnode.status = "active"
    cnode.save()
    return cnode


def update_ctasks(result):
    """ 根据id来更新mtasks """
    now = timezone.now()
    try:
        data = json.loads(base64.urlsafe_b64decode(str(result)))
    except:
        data = {}

    url, name, category, ttype = (data.get("url"),
                                  data.get("name"),
                                  data.get("category"),
                                  data.get("ttype"))

    if any([not url, not name, not category, not ttype]):
        return None
    else:
        ct, flag = CrawlerTasks.objects.get_or_create(url=url,
                                                      ttype=ttype,
                                                      name=name,
                                                      category=category)
        # 创建的记录
        if flag:
            ct.created_on = now
            if "parent_category" in data:
                ct.parent_category = data.get("parent_category")

            # 更新任务来源
            ct.source = data.get("source")
            queue = settings.TASK_QUEUE_MAPPER.get("task").get(ct.source)
            if not queue:
                return None

            # 将任务发送到消息队列
            rop.add_task_queue(queue, str(ct.id))
        else:
            # 没有content，并且原文内容为空时，认为没抓取到
            # 这是由于有一些页面确实没有内容
            if not data.get("content") and not data.get("page"):
                return None

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
