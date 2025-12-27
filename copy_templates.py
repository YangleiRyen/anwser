#!/usr/bin/env python
"""
将RPI计算器模板文件从项目级templates目录复制到应用级templates目录
"""

import os
import shutil

def copy_templates():
    # 源目录
    source_dir = 'templates/rpi_calculator'
    # 目标目录
    target_dir = 'rpi_calculator/templates/rpi_calculator'
    
    print(f"正在将模板文件从 {source_dir} 复制到 {target_dir}")
    
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 复制所有文件
    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        target_file = os.path.join(target_dir, filename)
        
        if os.path.isfile(source_file):
            shutil.copy2(source_file, target_file)
            print(f"复制文件: {filename}")
    
    print("模板文件复制完成！")

if __name__ == '__main__':
    copy_templates()
