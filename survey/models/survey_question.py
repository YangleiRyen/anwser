# survey/models/survey_question.py
from django.db import models


class SurveyQuestion(models.Model):
    """问卷问题关联模型 - 管理问卷和问题的关联关系"""
    survey = models.ForeignKey(
        'Survey',
        on_delete=models.CASCADE,
        related_name='survey_questions',
        verbose_name="所属问卷",
        db_index=True
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='survey_questions',
        verbose_name="问题",
        db_index=True
    )
    order = models.IntegerField(
        default=0,
        verbose_name="问题排序",
        help_text="数字越小，排序越靠前"
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="是否必填",
        help_text="如果启用，用户必须回答这个问题才能提交问卷"
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    
    # 添加分类字段，允许在问卷中为每个问题单独设置分类
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_questions',
        verbose_name="问题分类",
        help_text="可覆盖问题的原始分类"
    )
    
    class Meta:
        verbose_name = "问卷问题关联"
        verbose_name_plural = "问卷问题关联"
        ordering = ['survey', 'order']
        unique_together = ('survey', 'question')
        indexes = [
            models.Index(fields=['survey', 'order']),
        ]
    
    def __str__(self):
        return f"{self.survey.title[:20]} - {self.question.text[:30]}"
    
    def save(self, *args, **kwargs):
        """保存时，如果没有指定分类，使用问题的分类"""
        if not self.category and self.question.category:
            self.category = self.question.category
        super().save(*args, **kwargs)
    
    @property
    def display_category(self):
        """显示分类（优先使用问卷级别的分类）"""
        return self.category or self.question.category
