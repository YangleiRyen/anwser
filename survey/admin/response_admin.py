# survey/admin/response_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count

from ..models import Response


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    """回答记录管理"""
    list_display = ['survey', 'submit_time', 'wechat_nickname', 'completion_time', 'answer_count']
    list_filter = ['submit_time', 'survey']
    search_fields = ['wechat_nickname', 'wechat_openid', 'survey__title']
    readonly_fields = ['submit_time']
    list_select_related = ['survey']
    
    def has_add_permission(self, request):
        return False
    
    def answer_count(self, obj):
        return obj.answers.count()
    answer_count.short_description = '答案数量'
