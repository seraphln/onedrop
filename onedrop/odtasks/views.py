# coding=utf8
#


"""
onedrop首页相关接口
"""

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse

from onedrop.utils.redis_op import rop

from onedrop.utils import make_api_response

from onedrop.odtasks.funcs import update_ctasks

from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks


def get_crawler_task(source=None):
    """ 从任务队列获取一个采集任务 """
    queue = settings.TASK_QUEUE_MAPPER.get(source)
    if not queue:
        return None

    now = timezone.now()
    tid = rop.get_task_from_queue(queue=queue)
    if not tid:
        return []
    if source == "seed":
        seed = CrawlerSeeds.objects.filter(id=int(tid)).first()
        return update_and_return_seed(seed, now, status="running")
    else:
        ctask = CrawlerTasks.objects.filter(id=int(tid)).first()
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
    seed.name = seed.name.encode('utf8')
    return [seed,]


def update_crawler_task(request):
    """ 通过POST形式更新采集到的信息 """
    task_result = request.POST.get("task_result")
    update_ctasks(task_result)
    return make_api_response({})