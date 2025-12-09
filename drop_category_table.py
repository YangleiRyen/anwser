#!/usr/bin/env python
"""
删除现有category表的脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wechat_survey.settings")

import django
django.setup()

from django.db import connection

def drop_category_table():
    """删除现有category表"""
    print("开始删除survey_category表...")
    
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS survey_category")
    
    print("已成功删除survey_category表!")

if __name__ == "__main__":
    drop_category_table()
