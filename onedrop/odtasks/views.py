# coding=utf8
#


"""
onedrop首页相关接口
"""

from django.conf import settings
from django.utils import timezone

from onedrop.utils.redis_op import rop

from onedrop.utils import make_api_response

from onedrop.odtasks.funcs import update_ctasks

from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks


def get_crawler_task(queue="task", source=None):
    """ 从任务队列获取一个采集任务 """
    now = timezone.now()
    if queue == "seed":
        queue = settings.TASK_QUEUE_MAPPER.get(queue)
    else:
        queue = settings.TASK_QUEUE_MAPPER.get(queue).get(source)

    tid = rop.get_task_from_queue(queue=queue)
    if not tid:
        return []

    # 获取任务、更新任务状态返回任务实例
    tid = int(tid)
    if source == "seed":
        obj = CrawlerSeeds.objects.filter(id=tid).first()
    else:
        obj = CrawlerTasks.objects.filter(id=tid).first()

    return update_obj(obj, now, status="running")


def update_obj(obj, now, status=None):
    """ 更新给定的对象的last_crawl_on和status字段，并返回给定对象 """
    obj.last_crawl_on = now
    if status:
        obj.status = status

    obj.save()
    return [obj, ]


def update_crawler_task(request):
    """ 通过POST形式更新采集到的信息 """
    update_ctasks(request.POST.get("task_result"))
    return make_api_response({})