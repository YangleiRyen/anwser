#!/usr/bin/env python
"""
创建RPI计算器测试数据
包括授权码和测试问题
"""

import os
import sys
import random
from django.core.management.base import BaseCommand
from django.utils import timezone

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wechat_survey.settings')

# 导入Django模块
import django
django.setup()

# 导入模型
from rpi_calculator.models import AuthorizationCode, RPIQuestion

def create_authorization_codes():
    """创建测试授权码"""
    print("创建授权码...")
    codes = []
    for i in range(10):
        # 生成8位随机数字字母组合授权码
        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
        auth_code, created = AuthorizationCode.objects.get_or_create(
            code=code,
            defaults={'is_used': False}
        )
        if created:
            codes.append(code)
            print(f"创建授权码: {code}")
    return codes

def create_test_questions():
    """创建测试问题"""
    print("\n创建测试问题...")
    
    questions = [
        {
            "question_text": "我会经常查看伴侣的手机、社交媒体或聊天记录",
            "category": "信任与隐私",
            "question_order": 1
        },
        {
            "question_text": "当伴侣与异性朋友相处时，我会感到不安或嫉妒",
            "category": "嫉妒与安全感",
            "question_order": 2
        },
        {
            "question_text": "我希望伴侣能随时告诉我他们在哪里、在做什么",
            "category": "控制欲",
            "question_order": 3
        },
        {
            "question_text": "我会因为伴侣没有立即回复消息而感到焦虑",
            "category": "焦虑与依赖",
            "question_order": 4
        },
        {
            "question_text": "我认为伴侣应该优先考虑我的感受和需求",
            "category": "自我中心",
            "question_order": 5
        },
        {
            "question_text": "当伴侣有自己的兴趣爱好或社交活动时，我会感到被忽视",
            "category": "被忽视感",
            "question_order": 6
        },
        {
            "question_text": "我会试图影响伴侣的穿着、交友或职业选择",
            "category": "控制欲",
            "question_order": 7
        },
        {
            "question_text": "我害怕伴侣会离开我，所以会尽力讨好他们",
            "category": "安全感",
            "question_order": 8
        },
        {
            "question_text": "我会因为伴侣过去的感情经历而感到不舒服或耿耿于怀",
            "category": "过去经历",
            "question_order": 9
        },
        {
            "question_text": "我希望伴侣只属于我一个人，不与其他人分享他们的时间和精力",
            "category": "独占欲",
            "question_order": 10
        }
    ]
    
    for q_data in questions:
        question, created = RPIQuestion.objects.get_or_create(
            question_order=q_data['question_order'],
            defaults={
                'question_text': q_data['question_text'],
                'category': q_data['category']
            }
        )
        if created:
            print(f"创建问题 {q_data['question_order']}: {q_data['question_text'][:30]}...")

if __name__ == '__main__':
    print("开始创建RPI计算器测试数据...")
    
    # 创建授权码
    codes = create_authorization_codes()
    
    # 创建测试问题
    create_test_questions()
    
    print("\n测试数据创建完成！")
    print(f"生成的授权码: {', '.join(codes)}")
    print("请使用这些授权码进行测试。")
