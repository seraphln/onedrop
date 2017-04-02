# coding=utf-8
#


"""
1. 加载monitors
2. 将monitors中的任务拆分，写入到mtasks
3. 写入时检查mtask，如果有一条非finished的记录，那么不会创建新任务
"""

import os
import sys
from os.path import dirname, join
sys.path.append(join(dirname(__file__), '../'))
sys.path.append(join(dirname(__file__), '../../'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'anduin.settings'

import django
django.setup()

from datetime import datetime
from datetime import timedelta

from django.db.models import Q
from django.conf import settings

from anduin.adtasks import models

from anduin.utils.redis_op import rop


def backend():
    """ 加载monitors任务并写入到mtask中 """
    now = datetime.utcnow()
    monitors = models.Monitors.objects.filter(end_date__gte=now,
                                              is_expired=False)

    for monitor in monitors:
        for resume in monitor.resumes.all():
            mt = models.MTasks.objects.filter(~(Q(status="finished")), resume=resume).first()
            queue = settings.QUEUE_MAPPER.get(resume.source)
            if mt:
                print queue, str(mt.id)
                #print rop.add_task_queue(queue, str(mt.id))
                continue
            else:
                delta_time = now - timedelta(hours=12)
                if not queue:
                    continue

                mt = models.MTasks.objects.filter(status="finished",
                                                  resume=resume,
                                                  source=resume.source,
                                                  monitor=monitor,
                                                  created_on__gte=delta_time).first()
                if mt:
                    continue

                mt = models.MTasks(status="pending",
                                   resume=resume,
                                   source=resume.source,
                                   monitor=monitor,
                                   created_on=now,
                                   modified_on=now)
                mt.save()
                rop.add_task_queue(queue, str(mt.id))


if __name__ == "__main__":
    backend()