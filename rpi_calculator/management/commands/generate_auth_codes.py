#!/usr/bin/env python
"""
Django管理命令：生成授权码
支持按批次生成一定数量的授权码
"""

import random
from django.core.management.base import BaseCommand
from rpi_calculator.models import AuthorizationCode

class Command(BaseCommand):
    """生成授权码的管理命令"""
    help = '生成指定数量的授权码'
    
    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '-n', '--number', 
            type=int, 
            default=10, 
            help='生成授权码的数量，默认10个'
        )
        parser.add_argument(
            '-l', '--length',
            type=int,
            default=8,
            help='授权码长度，默认8位'
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='',
            help='授权码前缀'
        )
    
    def handle(self, *args, **options):
        """命令处理逻辑"""
        number = options['number']
        length = options['length']
        prefix = options['prefix']
        
        self.stdout.write(f'开始生成 {number} 个授权码，长度 {length} 位，前缀 "{prefix}"')
        
        # 生成字符集
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        generated_codes = []
        duplicate_count = 0
        max_attempts = number * 5  # 最大尝试次数，防止死循环
        attempts = 0
        
        while len(generated_codes) < number and attempts < max_attempts:
            attempts += 1
            # 生成随机部分
            random_part = ''.join(random.choices(chars, k=length - len(prefix)))
            # 组合成完整授权码
            code = f'{prefix}{random_part}'
            
            # 检查是否已存在
            if not AuthorizationCode.objects.filter(code=code).exists():
                # 创建授权码
                auth_code = AuthorizationCode.objects.create(code=code, is_used=False)
                generated_codes.append(code)
                self.stdout.write(self.style.SUCCESS(f'生成授权码: {code}'))
            else:
                duplicate_count += 1
                if duplicate_count % 100 == 0:
                    self.stdout.write(self.style.WARNING(f'已尝试 {duplicate_count} 次重复，正在继续...'))
        
        if len(generated_codes) < number:
            self.stdout.write(self.style.ERROR(f'生成失败：只生成了 {len(generated_codes)} 个授权码，达到最大尝试次数'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n生成完成！共生成 {len(generated_codes)} 个授权码'))
            self.stdout.write(f'已避免 {duplicate_count} 次重复')
            self.stdout.write('\n生成的授权码：')
            for i, code in enumerate(generated_codes, 1):
                self.stdout.write(f'{i}. {code}')
