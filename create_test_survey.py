# create_test_survey.py
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wechat_survey.settings')
django.setup()

from django.contrib.auth.models import User
from survey.models import Survey, Question, SurveyQuestion, Category, Option

# 创建测试用户
try:
    user = User.objects.create_user('testuser', 'test@example.com', 'test123')
except:
    user = User.objects.get(username='testuser')

# 创建测试分类
Category.objects.filter(name="用户体验").delete()
category = Category.objects.create(
    name="用户体验",
    slug="user-experience",
    description="关于用户体验的问题",
    is_active=True
)

# 创建测试问卷
# 先删除旧问卷，确保重新创建
Survey.objects.filter(title="用户满意度调查").delete()

survey = Survey.objects.create(
    title="用户满意度调查",
    description='请花几分钟时间告诉我们您对我们的产品和服务的看法',
    created_by=user,
    is_active=True
)

print(f"创建问卷: {survey.title}")

# 创建问题
questions_data = [
    {
        'text': '您对我们的产品整体满意度如何？',
        'question_type': 'rating',
        'order': 1,
        'is_required': True,
        'options': []
    },
    {
        'text': '您是通过什么渠道知道我们的？',
        'question_type': 'single_choice',
        'order': 2,
        'is_required': True,
        'options': [
            {'value': 'friend', 'label': '朋友推荐'},
            {'value': 'ad', 'label': '广告'},
            {'value': 'search', 'label': '搜索引擎'},
            {'value': 'social', 'label': '社交媒体'},
            {'value': 'other', 'label': '其他'}
        ]
    },
    {
        'text': '您喜欢我们产品的哪些方面？（可多选）',
        'question_type': 'multiple_choice',
        'order': 3,
        'is_required': False,
        'options': [
            {'value': 'design', 'label': '产品设计'},
            {'value': 'quality', 'label': '产品质量'},
            {'value': 'price', 'label': '价格合理'},
            {'value': 'service', 'label': '客户服务'},
            {'value': 'function', 'label': '功能实用'}
        ]
    },
    {
        'text': '您有什么建议或意见？',
        'question_type': 'text',
        'order': 4,
        'is_required': False,
        'options': []
    }
]

created_questions = 0
for q_data in questions_data:
    # 提取选项数据
    options_data = q_data.pop('options')
    # 提取order和is_required，用于SurveyQuestion
    order = q_data.pop('order')
    is_required = q_data.pop('is_required')
    
    # 创建问题，添加category关联，不直接关联survey
    question = Question.objects.create(
        category=category,
        created_by=user,
        is_public=True,
        **q_data
    )
    created_questions += 1
    
    # 通过中间表关联到问卷
    SurveyQuestion.objects.create(
        survey=survey,
        question=question,
        order=order,
        is_required=is_required,
        category=category
    )
    
    # 创建选项
    for i, option_data in enumerate(options_data, 1):
        Option.objects.create(
            question=question,
            value=option_data['value'],
            label=option_data['label'],
            order=i
        )

print(f"创建了 {created_questions} 个问题")
print(f"问卷ID: {survey.id}")
print(f"测试问卷已创建完成，可以访问 http://127.0.0.1:8000/survey/{survey.id}/ 进行测试")