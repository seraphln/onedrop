# coding=utf-8
#


"""
onedrop的自定义用户模块
"""

from __future__ import unicode_literals

from django.utils import timezone

from django.db import models

from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser


class UserManager(BaseUserManager):

    def create_user(self, name, password=None):
        user = self.model(name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None):
        user = self.create_user(name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class BaseUserInfo(models.Model):
    """ 基本用户信息模块 """
    avatar = models.URLField(verbose_name=u"用户头像", blank=True, null=True)


class OdUser(AbstractBaseUser, BaseUserInfo):
    """ Oduin模块的自定义用户模型 """
    name = models.CharField(max_length=32, unique=True, verbose_name=u"昵称")
    created_on = models.DateTimeField(default=timezone.now,
                                      verbose_name=u"创建时间")
    modified_on = models.DateTimeField(default=timezone.now,
                                       verbose_name=u"最后一次修改时间")
    is_admin = models.BooleanField(default=False, verbose_name=u"是否是管理员")
    is_delete = models.BooleanField(default=False, verbose_name=u"是否删除")
    is_active = models.BooleanField(default=True, verbose_name=u"是否激活")

    objects = UserManager()

    USERNAME_FIELD = "name"
    #REQUIRED_FIELDS = ("name", )

    def __unicode__(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        ordering = ("-created_on", )
        verbose_name = u"OneDrop用户模块"
        verbose_name_plural = u"OneDrop用户模块"
