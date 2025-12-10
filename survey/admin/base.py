# survey/admin/base.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class CustomAdminSite(admin.AdminSite):
    """自定义Admin站点"""
    site_header = _('问卷调查管理系统')
    site_title = _('问卷调查后台')
    index_title = _('系统管理')
    
    def get_app_list(self, request, app_label=None):
        """重写应用列表排序，将问卷应用放在最前面"""
        # 获取默认的应用列表
        app_list = super().get_app_list(request, app_label)
        
        # 创建一个新的应用列表，将'问卷'应用移到最前面
        new_app_list = []
        other_apps = []
        
        for app in app_list:
            if app['name'] == _('问卷'):
                new_app_list.append(app)
            else:
                other_apps.append(app)
        
        # 将其他应用添加到后面
        new_app_list.extend(other_apps)
        
        return new_app_list


# 替换默认的admin.site
admin.site.__class__ = CustomAdminSite
