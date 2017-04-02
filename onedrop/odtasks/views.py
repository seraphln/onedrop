# coding=utf8
#


"""
onedrop首页相关接口
"""

import json

from django.conf import settings
from django.utils import timezone

from onedrop.utils import make_api_response

from django.views.generic import View

from onedrop.utils.redis_op import rop

from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks
from onedrop.odtasks.funcs import create_crawler_task_detail


def get_crawl_task(source=None):
    """ 从任务队列获取一个采集任务 """
    if not source:
        return None

    now = timezone.now()
    tid = rop.get_task_from_queue(queue=source)
    if not tid:
        return []
    if source == "seed":
        seed = CrawlerSeed.objects.filter(id=int(tid)).first()
        return update_and_return_seed(seed, now, status="running")
    else:
        ctask = CrawlerTaskDetail.objects.filter(id=int(tid)).first()
        return update_and_return_ctask(ctask, now, status="running")


def update_and_return_ctask(ctask, now, status=None):
    """ 更新给定的mtask并返回 """
    ctask.last_crawl_on = now
    if status:
        ctask.status = status
    ctask.save()
    return [ctask,]


def update_and_return_seed(seed, now, status=None):
    """ 更新给定的mtask并返回 """
    seed.last_crawl_on = now
    if status:
        seed.status = status
    seed.save()
    return [seed,]