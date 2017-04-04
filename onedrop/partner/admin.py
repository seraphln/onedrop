# coding=utf8
#


from django.contrib import admin
from onedrop.partner.models import App


class AppAdmin(admin.ModelAdmin):
    """ 第三方应用的后台管理页面 """
    list_display = ("id", "name", "is_active",
                    "access_key", "secret_key",
                    "created_on", "modified_on")
    search_fields = ("name", "is_active", "access_key")


admin.site.register(App, AppAdmin)
