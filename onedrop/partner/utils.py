# coding=utf8
#

from onedrop.partner.models import App


def check_permission(context):
    """ 检查权限 """
    ak = context.META.get("HTTP_X_AUTH_ACCESS_KEY")
    app = App.objects.filter(access_key=ak, is_active=True).first()
    if not app:
        return None
    else:
        return app
