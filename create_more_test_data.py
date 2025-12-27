#!/usr/bin/env python
"""
创建更多RPI计算器测试数据
"""

import os
import sys
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wechat_survey.settings')

# 导入Django模块
import django
django.setup()

# 导入模型
from rpi_calculator.models import AuthorizationCode

def create_more_authorization_codes():
    """创建更多测试授权码"""
    print("创建更多授权码...")
    codes = []
    for i in range(5):
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

if __name__ == '__main__':
    print("开始创建更多RPI计算器测试数据...")
    
    # 创建更多授权码
    codes = create_more_authorization_codes()
    
    print(f"\n新生成的授权码: {', '.join(codes)}")
    print("\n所有可用授权码:")
    
    # 显示所有未使用的授权码
    unused_codes = AuthorizationCode.objects.filter(is_used=False)
    for code in unused_codes:
        print(f"- {code.code}")
    
    print(f"\n总共有 {unused_codes.count()} 个可用授权码")
