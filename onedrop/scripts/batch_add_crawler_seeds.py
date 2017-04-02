# coding=utf8
#


"""
批量将采集任务的种子信息放到对应的采集队列里
"""

# 添加django的环境变量
import os
import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'onedrop.settings'

import django
django.setup()


from datetime import datetime
from datetime import timedelta

from onedrop.odtasks.models import CrawlerSeeds

from onedrop.utils.redis_op import rop


def backend():
    """ 加载爬虫种子信息到redis """
    now = datetime.utcnow()
    seeds = CrawlerSeeds.objects.filter()

    for seed in seeds:
        seed.status = "crawling"
        seed.modified_on = now
        seed.last_crawl_on = now
        seed.save()

        print "Putting %s to redis" % seed.name

        rop.add_task_queue("onedrop.crawler.seed", str(seed.id))
        rop.add_task_queue("seed", str(seed.id))


if __name__ == "__main__":
    backend()
