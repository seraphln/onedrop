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

from onedrop.util.redis_op import rop

from onedrop.odtasks.models import CrawlerSeed
from onedrop.odtasks.models import CrawlerTaskDetail
from onedrop.odtasks.models import create_crawler_task_detail


class CrawlerTaskManager(View):
    """ 采集任务管理 """
    model_cls = CrawlerSeed

    def get(self, request, ttype, *args, **kwargs):
        """ 从redis任务队列中获取一个新的需要采集的seed """
        queue = settings.TASK_QUEUE.get("ttype")
        if not queue:
            return make_api_response({})
        else:
            task = rop.get_task_from_queue(queue)
            return make_api_response(task)


class CrawlerURLManager(View):
    """ 采集任务的URL管理集合 """

    model_cls = CrawlerTaskDetail

    def get(self, request, ttype, *args, **kwargs):
        """ 从redis任务队列获取一个新的需要采集的url """
        task = rop.get_task_from_queue("detail")
        return make_api_response(task)

    def post(self, request, *args, **kwargs):
        """ 创建一个新的采集URL """
        name = kwargs.get("name")
        ttype = kwargs.get("ttype")
        url = kwargs.get("url")
        parent_cate = kwargs.get("parent_cate", None)
        status = kwargs.get("status", "")

        ct = create_crawler_task_detail(name, ttype, url, parent_cate, status)
        if status == "pending":
            task = {"name": name,
                    "ttype": ttype,
                    "url": "url",
                    "parent_cate": parent_cate}
            rop.add_task_queue("detail", json.dumps(task))
        return make_api_response(ct)


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