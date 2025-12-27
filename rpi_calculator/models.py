from django.db import models

# Create your models here.

class AuthorizationCode(models.Model):
    """
    授权码模型
    用于验证用户是否有权限进行测试
    """
    code = models.CharField(max_length=8, unique=True, verbose_name="授权码")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "授权码"
        verbose_name_plural = "授权码"
        db_table = "rpi_authorization_code"

    def __str__(self):
        return self.code


class RPIUser(models.Model):
    """
    RPI测试用户模型
    存储用户基本信息和测试记录
    """
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
    )

    AGE_RANGE_CHOICES = (
        ('18-24', '18-24岁'),
        ('25-29', '25-29岁'),
        ('30-34', '30-34岁'),
        ('35-39', '35-39岁'),
        ('40-49', '40-49岁'),
        ('50+', '50岁以上'),
    )

    RELATIONSHIP_STATUS_CHOICES = (
        ('single', '单身'),
        ('in_relationship', '恋爱中'),
        ('married', '已婚'),
        ('divorced', '离婚'),
        ('widowed', '丧偶'),
    )

    TEST_TYPE_CHOICES = (
        ('self', '给自己测'),
        ('partner', '为恋人测'),
    )

    # 用户基本信息
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name="昵称")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="性别")
    age_range = models.CharField(max_length=10, choices=AGE_RANGE_CHOICES, blank=True, null=True, verbose_name="年龄段")
    relationship_status = models.CharField(max_length=20, choices=RELATIONSHIP_STATUS_CHOICES, blank=True, null=True, verbose_name="恋爱状态")
    test_type = models.CharField(max_length=10, choices=TEST_TYPE_CHOICES, blank=True, null=True, verbose_name="测试类型")

    # 授权码关联
    authorization_code = models.OneToOneField(AuthorizationCode, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="授权码")

    # 测试时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "RPI测试用户"
        verbose_name_plural = "RPI测试用户"
        db_table = "rpi_user"

    def __str__(self):
        return f"RPI User {self.id}"


class RPITestResult(models.Model):
    """
    RPI测试结果模型
    存储用户测试的详细结果和得分
    """
    user = models.OneToOneField(RPIUser, on_delete=models.CASCADE, related_name="test_result", verbose_name="用户")
    total_score = models.IntegerField(verbose_name="总分")
    score_level = models.CharField(max_length=20, verbose_name="得分等级")
    summary = models.TextField(verbose_name="结果总结")
    detailed_analysis = models.TextField(verbose_name="详细分析")
    suggestions = models.TextField(verbose_name="建议")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "RPI测试结果"
        verbose_name_plural = "RPI测试结果"
        db_table = "rpi_test_result"

    def __str__(self):
        return f"Test Result for User {self.user.id}"


class RPIQuestion(models.Model):
    """
    RPI测试问题模型
    存储测试中的问题
    """
    question_text = models.TextField(verbose_name="问题内容")
    question_order = models.IntegerField(verbose_name="问题顺序")
    category = models.CharField(max_length=50, verbose_name="问题类别")

    class Meta:
        verbose_name = "RPI测试问题"
        verbose_name_plural = "RPI测试问题"
        db_table = "rpi_question"
        ordering = ['question_order']

    def __str__(self):
        return f"Question {self.question_order}: {self.question_text[:50]}..."


class RPIAnswer(models.Model):
    """
    RPI测试答案模型
    存储用户对每个问题的回答
    """
    user = models.ForeignKey(RPIUser, on_delete=models.CASCADE, related_name="answers", verbose_name="用户")
    question = models.ForeignKey(RPIQuestion, on_delete=models.CASCADE, verbose_name="问题")
    score = models.IntegerField(verbose_name="得分")
    answer_text = models.TextField(verbose_name="答案内容")

    class Meta:
        verbose_name = "RPI测试答案"
        verbose_name_plural = "RPI测试答案"
        db_table = "rpi_answer"

    def __str__(self):
        return f"Answer from User {self.user.id} to Question {self.question.question_order}"