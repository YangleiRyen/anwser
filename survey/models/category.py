# survey/models/category.py
from django.db import models


class Category(models.Model):
    """问题分类模型 - 可在后台管理"""
    name = models.CharField(
        max_length=100,
        verbose_name="分类名称",
        unique=True,
        help_text="分类的唯一名称"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="分类标识",
        help_text="用于URL的分类标识"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="分类描述",
        help_text="可选，填写分类的详细说明"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否激活",
        help_text="只有激活的分类才能使用"
    )
    
    class Meta:
        verbose_name = "问题分类"
        verbose_name_plural = "问题分类管理"
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({'激活' if self.is_active else '停用'})"
    
    @property
    def questions_count(self):
        """获取该分类下的问题数量"""
        return self.questions.count()
