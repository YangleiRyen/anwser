# survey/admin/answer_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count

from ..models import Answer


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """答案管理"""
    list_display = ['question_preview', 'survey_preview', 'response', 'answer_preview']
    list_filter = ['response__survey', 'question__question_type']
    search_fields = ['answer_text', 'question__text', 'response__wechat_nickname']
    list_select_related = ['question', 'response__survey']
    
    def question_preview(self, obj):
        return obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
    question_preview.short_description = '问题'
    
    def survey_preview(self, obj):
        return obj.response.survey.title
    survey_preview.short_description = '问卷'
    
    def answer_preview(self, obj):
        """答案预览，处理各种类型的答案"""
        if obj.answer_text:
            return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
        elif obj.answer_choice:
            if obj.question.question_type in ['single_choice', 'multiple_choice']:
                choices = obj.answer_choice if isinstance(obj.answer_choice, list) else [obj.answer_choice]
                
                # 创建选项映射
                option_map = {option.value: option.label for option in obj.question.options.all()}
                
                # 转换值为标签
                labels = [option_map.get(choice, choice) for choice in choices]
                return ', '.join(labels)
            return str(obj.answer_choice)
        return '-'
    answer_preview.short_description = '答案'
