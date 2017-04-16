# coding=utf8
#


"""
onedrop项目的异步任务集合
"""

from celery import task

from datetime import datetime
from datetime import timedelta

from onedrop.utils.redis_op import rop

from onedrop.odtasks.models import CrawlerSeeds
from onedrop.odtasks.models import CrawlerTasks


@task()
def cron_add_pcbaby_tasks_weekly():
    """
        每周将pcbaby的任务写入到数据采集的队列里
    """
    now = datetime.utcnow()
    seeds = CrawlerSeeds.objects.filter()

    for seed in seeds:
        seed.modified_on = now
        seed.last_crawl_on = now
        seed.status = "crawling"
        seed.save()

        rop.add_task_queue("onedrop.crawler.seed", str(seed.id))