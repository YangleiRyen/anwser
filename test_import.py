from survey.models import Question, Category, Option
from django.contrib.auth.models import User
import re

# 获取或创建测试用户
user = User.objects.first()
if not user:
    user = User.objects.create_user(username='testuser', password='testpassword')

# 获取或创建测试分类
category, _ = Category.objects.get_or_create(name='测试分类')

# 创建测试问题
question = Question.objects.create(
    text='测试多选题',
    question_type='multiple_choice',
    category=category,
    created_by=user,
    is_public=True
)

# 测试只包含标签的选项导入
options_str = '选项1;选项2;选项3'
options = options_str.split(';')

for i, option in enumerate(options):
    label = option.strip()
    if label:
        # 自动生成值
        value = re.sub(r'[^\w\s]', '', label)
        value = value.lower().replace(' ', '_')
        if not value:
            value = f'option_{i+1}'
        
        # 创建选项
        Option.objects.create(
            question=question,
            value=value,
            label=label,
            order=i
        )
        print(f'创建选项: 值={value}, 标签={label}')

print('测试成功！')