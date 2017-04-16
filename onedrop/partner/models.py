# coding=utf8
#


"""
第三方合作用到的接口
所有的API请求都要经过auth模块的检查
主要检查的是access_key是否一致
"""

from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils import timezone

from onedrop.odauth.models import OdUser


def generate_key():
    """ 生成RSA密钥 """
    return uuid.uuid4().hex


class App(models.Model):
    """ 第三方合作App管理 """
    name = models.CharField(max_length=128, verbose_name=u"第三方应用名称")
    is_active = models.BooleanField(default=False, verbose_name=u"应用是否激活")
    access_key = models.CharField(max_length=64,
                                  null=True,
                                  blank=True,
                                  verbose_name=u"第三方应用的ak")
    secret_key = models.CharField(max_length=64,
                                  null=True,
                                  blank=True,
                                  verbose_name=u"第三方应用的sk")
    user = models.ForeignKey(OdUser, verbose_name=u"第三方应用创建人")
    created_on = models.DateTimeField(default=timezone.now,
                                      verbose_name=u"第三方应用创建时间")
    modified_on = models.DateTimeField(default=timezone.now,
                                       verbose_name=u"第三方应用修改时间")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"第三方应用"
        verbose_name_plural = u"第三方应用"

    def save(self, *args, **kwargs):
        """ 重写save方法，在save时，判断如果没有ak的话，则更新ak和sk """
        if not self.access_key:
            self.access_key = generate_key()
            self.secret_key = generate_key()

        return super(App, self).save(*args, **kwargs)
