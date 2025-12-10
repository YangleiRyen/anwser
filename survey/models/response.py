# survey/models/response.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Response(models.Model):
    """问卷回答"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        'Survey',
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="问卷",
        db_index=True
    )
    respondent = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="回答者",
        related_name='survey_responses',
        db_index=True
    )
    session_key = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="会话标识",
        help_text="用于匿名用户的会话标识"
    )
    
    # 微信相关信息
    wechat_openid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="微信OpenID",
        db_index=True
    )
    wechat_unionid = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="微信UnionID",
        db_index=True
    )
    wechat_nickname = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="微信昵称"
    )
    
    # 提交信息
    submit_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="提交时间",
        db_index=True
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP地址"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="用户代理"
    )
    completion_time = models.IntegerField(
        default=0,
        verbose_name="完成用时（秒）",
        validators=[MinValueValidator(0), MaxValueValidator(86400)],  # 最多24小时
        help_text="从开始填写到提交的总用时（秒）"
    )
    
    class Meta:
        verbose_name = "回答记录"
        verbose_name_plural = "回答记录"
        ordering = ['-submit_time']
        indexes = [
            models.Index(fields=['survey', 'submit_time']),
            models.Index(fields=['wechat_openid', 'survey']),
        ]
    
    def __str__(self):
        identifier = self.get_respondent_identifier()
        return f"{self.survey.title[:20]} - {identifier} - {self.submit_time:%Y-%m-%d %H:%M}"
    
    def get_respondent_identifier(self):
        """获取回答者标识"""
        if self.respondent:
            return self.respondent.username
        elif self.wechat_nickname:
            return self.wechat_nickname
        elif self.session_key:
            return f"匿名({self.session_key[:8]})"
        return "未知用户"
    
    @property
    def is_anonymous(self):
        """是否为匿名回答"""
        return not bool(self.respondent)
    
    @property
    def is_complete(self):
        """检查回答是否完整（回答了所有必填问题）"""
        required_questions = self.survey.survey_questions.filter(is_required=True)
        answered_questions = set(self.answers.values_list('question_id', flat=True))
        
        for sq in required_questions:
            if sq.question_id not in answered_questions:
                return False
        return True
