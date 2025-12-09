# survey/models.py
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
        Category,
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


class SurveyQuestion(models.Model):
    """问卷问题关联模型 - 管理问卷和问题的关联关系"""
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='survey_questions',
        verbose_name="所属问卷",
        db_index=True
    )
    question = models.ForeignKey(
        Question,
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
        Category,
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


class Response(models.Model):
    """问卷回答"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        Survey,
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


class Answer(models.Model):
    """单个问题的回答"""
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="所属回答",
        db_index=True
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="问题",
        db_index=True
    )
    answer_text = models.TextField(
        blank=True,
        verbose_name="回答文本",
        help_text="用于文本题的回答"
    )
    answer_choice = models.JSONField(
        default=list,
        blank=True,
        verbose_name="选择答案",
        help_text="用于选择题的回答（JSON格式）"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="回答时间")
    
    class Meta:
        verbose_name = "答案"
        verbose_name_plural = "答案"
        ordering = ['response', 'question__survey_questions__order']
        unique_together = ('response', 'question')
        indexes = [
            models.Index(fields=['response', 'question']),
        ]
    
    def __str__(self):
        answer_display = self.get_answer_display()
        return f"{self.question.text[:30]}: {answer_display[:30]}"
    
    def get_answer_display(self):
        """获取答案的显示文本"""
        if self.answer_text:
            return self.answer_text
        
        if self.answer_choice:
            # 处理选择题答案
            if self.question.is_choice_question:
                choices = self.answer_choice if isinstance(self.answer_choice, list) else [self.answer_choice]
                labels = [self.question.get_option_label(choice) for choice in choices]
                return ', '.join(labels)
            return str(self.answer_choice)
        
        return "未回答"
    
    def clean(self):
        """数据验证"""
        from django.core.exceptions import ValidationError
        
        if not self.answer_text and not self.answer_choice:
            raise ValidationError("必须提供答案文本或选择答案")
        
        # 验证选择题答案是否在选项范围内
        if self.question.is_choice_question and self.answer_choice:
            valid_values = set(self.question.options.values_list('value', flat=True))
            choices = self.answer_choice if isinstance(self.answer_choice, list) else [self.answer_choice]
            
            for choice in choices:
                if choice not in valid_values:
                    raise ValidationError(f"选项 '{choice}' 不在有效选项范围内")
    
    def save(self, *args, **kwargs):
        """保存前进行数据清理和验证"""
        self.clean()
        super().save(*args, **kwargs)


class QRCode(models.Model):
    """二维码管理"""
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='qrcodes',
        verbose_name="对应问卷",
        db_index=True
    )
    name = models.CharField(
        max_length=100,
        verbose_name="二维码名称",
        help_text="便于识别的二维码名称"
    )
    short_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="短代码",
        db_index=True,
        help_text="用于生成短链接的唯一代码"
    )
    scan_count = models.IntegerField(
        default=0,
        verbose_name="扫描次数",
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "二维码"
        verbose_name_plural = "二维码"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['short_code']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.survey.title[:20]}"
    
    @property
    def short_url(self):
        """获取短链接（需要根据实际URL配置调整）"""
        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        return f"{base_url}/qr/{self.short_code}"
    
    def increment_scan_count(self):
        """增加扫描次数"""
        self.scan_count = models.F('scan_count') + 1
        self.save(update_fields=['scan_count'])