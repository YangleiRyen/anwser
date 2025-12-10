# survey/models/question.py
from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    """问题模型 - 问题库"""
    QUESTION_TYPE_TEXT = 'text'
    QUESTION_TYPE_SINGLE_CHOICE = 'single_choice'
    QUESTION_TYPE_MULTIPLE_CHOICE = 'multiple_choice'
    QUESTION_TYPE_RATING = 'rating'
    QUESTION_TYPE_DATE = 'date'
    
    QUESTION_TYPES = (
        (QUESTION_TYPE_TEXT, '文本题'),
        (QUESTION_TYPE_SINGLE_CHOICE, '单选题'),
        (QUESTION_TYPE_MULTIPLE_CHOICE, '多选题'),
        (QUESTION_TYPE_RATING, '评分题'),
        (QUESTION_TYPE_DATE, '日期题'),
    )
    
    text = models.TextField(
        verbose_name="问题内容",
        help_text="输入问题的完整描述"
    )
    question_type = models.CharField(
        max_length=50,
        choices=QUESTION_TYPES,
        verbose_name="问题类型",
        db_index=True
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions',
        verbose_name="问题分类",
        help_text="选择问题的分类"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="创建者",
        related_name='questions',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_public = models.BooleanField(
        default=True,
        verbose_name="是否公开",
        help_text="公开的问题可以被所有用户使用"
    )
    
    class Meta:
        verbose_name = "问题"
        verbose_name_plural = "问题库"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['question_type', 'is_public']),
            models.Index(fields=['category', 'created_at']),
        ]
    
    def __str__(self):
        category_name = self.category.name if self.category else '未分类'
        type_display = self.get_question_type_display()
        return f"[{category_name}][{type_display}] {self.text[:50]}"
    
    @property
    def is_choice_question(self):
        """判断是否为选择题"""
        return self.question_type in [
            self.QUESTION_TYPE_SINGLE_CHOICE,
            self.QUESTION_TYPE_MULTIPLE_CHOICE
        ]
    
    @property
    def options_list(self):
        """获取选项列表（仅限选择题）"""
        if self.is_choice_question:
            return list(self.options.values('value', 'label').order_by('order'))
        return []
    
    def get_option_label(self, value):
        """根据选项值获取标签"""
        try:
            option = self.options.get(value=value)
            return option.label
        except Option.DoesNotExist:
            return value


class Option(models.Model):
    """问题选项模型"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="所属问题",
        db_index=True
    )
    value = models.CharField(
        max_length=100,
        verbose_name="选项值",
        help_text="用于存储和识别的值（英文或数字）"
    )
    label = models.CharField(
        max_length=200,
        verbose_name="选项标签",
        help_text="显示给用户看到的选项文本"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="选项排序",
        help_text="数字越小，排序越靠前"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "选项"
        verbose_name_plural = "选项"
        ordering = ['question', 'order']
        unique_together = ('question', 'value')
        indexes = [
            models.Index(fields=['question', 'order']),
        ]
    
    def __str__(self):
        question_text = self.question.text[:30]
        return f"{question_text} - {self.label}"
    
    def save(self, *args, **kwargs):
        """保存时自动清理空白字符"""
        self.value = self.value.strip()
        self.label = self.label.strip()
        super().save(*args, **kwargs)
