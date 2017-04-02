# coding=utf-8


from django.contrib import admin

from onedrop.odauth.models import OdUser


class OdUserAdmin(admin.ModelAdmin):
    """ 自定义的用户模块 """
    list_display = ("name", "is_admin", "is_delete", "is_active")
    search_fields = ("name", )


admin.site.register(OdUser, OdUserAdmin)
