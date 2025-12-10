# survey/models/survey.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Survey(models.Model):
    """问卷模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200,
        verbose_name="问卷标题",
        help_text="输入问卷的标题，最多200个字符"
    )
    description = models.TextField(
        verbose_name="问卷描述",
        blank=True,
        help_text="可选，填写问卷的详细说明"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="创建者",
        related_name='surveys',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否激活",
        help_text="只有激活的问卷才能被访问"
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="开始时间",
        help_text="问卷开始的时间，留空表示立即开始"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="结束时间",
        help_text="问卷结束的时间，留空表示不限制"
    )
    
    # 微信相关设置
    require_wechat = models.BooleanField(
        default=False,
        verbose_name="必须微信打开",
        help_text="如果启用，只能通过微信访问问卷"
    )
    allow_anonymous = models.BooleanField(
        default=True,
        verbose_name="允许匿名",
        help_text="是否允许未登录用户提交问卷"
    )
    limit_per_user = models.IntegerField(
        default=1,
        verbose_name="每人提交限制",
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="每个用户最多可提交的次数"
    )
    
    class Meta:
        verbose_name = "问卷"
        verbose_name_plural = "问卷"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({'激活' if self.is_active else '停用'})"
    
    @property
    def is_available(self):
        """检查问卷是否可用（在有效期内且激活）"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.start_date and now < self.start_date:
            return False
            
        if self.end_date and now > self.end_date:
            return False
            
        return True
    
    @property
    def questions_count(self):
        """获取问卷中的问题数量"""
        return self.survey_questions.count()
    
    @property
    def responses_count(self):
        """获取问卷的提交数量"""
        return self.responses.count()
