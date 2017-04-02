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

from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks


def create_crawler_task_detail(name,
                               ttype,
                               url,
                               parent_cate=None,
                               status="pending"):
    """ 根据给定的参数创建crawler结果 """
    now = timezone.now()
    ct, flag = CrawlerTasks.objects.get_or_create(name=name,
                                                  ttype=ttype,
                                                  url=url,
                                                  parent_cate=parent_cate)
    # 新创建记录
    if flag:
        ct.created_on = now
        ct.modified_on = now
    else:
        ct.modified_on = now

    ct.status = status
    ct.save()

    return ct


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
        queue = "onedrop.crawler.task"
        ct, flag = CrawlerTasks.objects.get_or_create(url=url,
                                                      ttype=ttype,
                                                      name=name,
                                                      category=category)
        # 创建的记录
        if flag:
            if "parent_category" in data:
                ct.parent_category = data.get("parent_category")
            ct.created_on = now
            ct.modified_on = now
            ct.status = "pending"
            rop.add_task_queue(queue, str(ct.id))
        else:
            if not data.get("content"):
                return None

            ct.status = "finished"
            ct.content = data.get("content")
            ct.result = data.get("result")
            ct.page = data.get("page")
            ct.last_crawl_on = now
            ct.modified_on = now

        ct.save()
        ct.name = ct.name.encode('utf8')
        return ct
