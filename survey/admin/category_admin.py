# survey/admin/category_admin.py
from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from ..models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """问题分类管理"""
    list_display = ['name', 'slug', 'is_active', 'created_at', 'question_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fields = ['name', 'slug', 'description', 'is_active']
    ordering = ['-created_at']
    actions = ['make_active', 'make_inactive']
    
    def get_queryset(self, request):
        """优化查询集，预加载相关问题计数"""
        return super().get_queryset(request).annotate(
            _question_count=Count('questions')
        )
    
    def question_count(self, obj):
        """统计该分类下的问题数量"""
        return obj._question_count if hasattr(obj, '_question_count') else obj.questions.count()
    question_count.short_description = '问题数量'
    question_count.admin_order_field = '_question_count'
    
    def make_active(self, request, queryset):
        """批量激活选中的分类"""
        queryset.update(is_active=True)
    make_active.short_description = '批量激活分类'
    
    def make_inactive(self, request, queryset):
        """批量停用选中的分类"""
        queryset.update(is_active=False)
    make_inactive.short_description = '批量停用分类'
