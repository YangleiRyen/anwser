# survey/admin/survey_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django import forms
from django.shortcuts import render, redirect

from ..models import Survey, SurveyQuestion


class SurveyQuestionInline(admin.TabularInline):
    """问卷问题关联内联表单"""
    model = SurveyQuestion
    extra = 1
    ordering = ['order']
    fields = ['question', 'order', 'is_required']
    verbose_name = '问卷问题'
    verbose_name_plural = '问卷问题'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """优化问题选择框"""

        # 安全地获取 queryset
        queryset = kwargs.get('queryset')
        
        # 为特定字段过滤 queryset
        if db_field.name == "your_field_name":  # 替换为实际字段名
            # 如果 kwargs 中没有 queryset，则从模型获取
            if queryset is None:
                queryset = db_field.remote_field.model.objects.all()
            
            # 过滤 queryset
            queryset = queryset.filter(your_filter_condition=True)
            
            # 更新 kwargs
            kwargs['queryset'] = queryset
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """问卷管理"""
    list_display = ['title', 'created_by', 'created_at', 'is_active', 'response_count', 'view_statistics']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'statistics']
    inlines = [SurveyQuestionInline]
    list_select_related = ['created_by']
    
    # 优化查询集
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'responses', 'survey_questions__question'
        ).annotate(response_count=Count('responses'))
    
    # 自定义字段
    def response_count(self, obj):
        return obj.response_count if hasattr(obj, 'response_count') else obj.responses.count()
    response_count.short_description = '回答数量'
    response_count.admin_order_field = 'response_count'
    
    def view_statistics(self, obj):
        """查看详细统计的链接"""
        url = reverse('admin:survey_statistics', args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" target="_blank">查看统计</a>',
            url
        )
    view_statistics.short_description = '详细统计'
    
    def statistics(self, obj):
        """显示问卷统计信息"""
        total_responses = obj.responses.count()
        html = f"<h3>问卷统计</h3>"
        html += f"<p><strong>总回答数：</strong>{total_responses}</p>"
        
        survey_questions = obj.survey_questions.select_related('question').all()
        if survey_questions:
            html += "<h4>问题详情：</h4><ul>"
            for sq in survey_questions:
                answer_count = sq.question.answers.count()
                html += f"<li><strong>{sq.question.text}</strong> ({sq.question.get_question_type_display()})：{answer_count} 个回答</li>"
            html += "</ul>"
        
        return format_html(html)
    statistics.short_description = '统计信息'
    
    # 自定义URL和视图
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:pk>/statistics/', self.admin_site.admin_view(self.statistics_view), 
                 name='survey_statistics'),
        ]
        return custom_urls + urls
    
    def statistics_view(self, request, pk):
        """详细统计视图"""
        survey = self.get_object(request, pk)
        if not survey:
            self.message_user(request, '问卷不存在', 'error')
            return redirect(reverse('admin:survey_survey_changelist'))
        
        # 计算统计数据
        total_responses = survey.responses.count()
        survey_questions = survey.survey_questions.select_related('question').prefetch_related(
            'question__options', 'question__answers'
        ).all().order_by('order')
        
        questions_stats = []
        for sq in survey_questions:
            question = sq.question
            answers = question.answers.all()
            stats = self._calculate_question_stats(question, answers)
            questions_stats.append(stats)
        
        context = {
            **self.admin_site.each_context(request),
            'title': f'{survey.title} - 统计信息',
            'survey': survey,
            'total_responses': total_responses,
            'questions': questions_stats,
            'opts': self.model._meta,
        }
        
        return TemplateResponse(request, 'admin/survey/statistics.html', context)
    
    def _calculate_question_stats(self, question, answers):
        """计算问题统计数据"""
        stats = {
            'question': question,
            'answer_count': answers.count(),
            'type': question.question_type,
            'data': {},
            'options': []
        }
        
        if question.question_type in ['single_choice', 'multiple_choice']:
            # 选择题统计
            option_stats = {}
            for option in question.options.all():
                option_stats[option.value] = {
                    'label': option.label,
                    'count': 0,
                    'percentage': 0.0
                }
            
            for answer in answers:
                choices = answer.answer_choice
                if isinstance(choices, list):
                    for choice in choices:
                        if choice in option_stats:
                            option_stats[choice]['count'] += 1
                elif isinstance(choices, str) and choices in option_stats:
                    option_stats[choices]['count'] += 1
            
            total = answers.count() or 1
            for option_data in option_stats.values():
                option_data['percentage'] = (option_data['count'] / total) * 100
            
            stats['data'] = option_stats
            stats['options'] = list(question.options.all().values('value', 'label'))
            
        elif question.question_type == 'rating':
            # 评分题统计
            ratings = {}
            for i in range(1, 6):
                ratings[str(i)] = {'count': 0, 'percentage': 0.0}
            
            for answer in answers:
                rating = answer.answer_choice
                if isinstance(rating, list) and rating:
                    rating = rating[0]
                if isinstance(rating, str) and rating in ratings:
                    ratings[rating]['count'] += 1
            
            total = answers.count() or 1
            for rating_data in ratings.values():
                rating_data['percentage'] = (rating_data['count'] / total) * 100
            
            stats['data'] = ratings
            
        elif question.question_type == 'text':
            # 文本题统计
            text_answers = []
            for answer in answers[:10]:
                text = answer.answer_text[:100] + ('...' if len(answer.answer_text) > 100 else '')
                text_answers.append(text)
            stats['data'] = text_answers
        
        return stats
