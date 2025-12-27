from django.contrib import admin
from .models import AuthorizationCode, RPIUser, RPITestResult, RPIQuestion, RPIAnswer

# 注册授权码模型
@admin.register(AuthorizationCode)
class AuthorizationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'is_used', 'created_at', 'updated_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('code',)
    ordering = ('-created_at',)
    # 添加批量操作
    actions = ['mark_as_used', 'mark_as_unused', 'generate_new_codes']
    
    def mark_as_used(self, request, queryset):
        """批量标记为已使用"""
        queryset.update(is_used=True)
    mark_as_used.short_description = '标记为已使用'
    
    def mark_as_unused(self, request, queryset):
        """批量标记为未使用"""
        queryset.update(is_used=False)
    mark_as_unused.short_description = '标记为未使用'
    
    def generate_new_codes(self, request, queryset):
        """批量生成新授权码"""
        import random
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        # 默认生成10个授权码
        number = 10
        length = 8
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        generated_count = 0
        for _ in range(number):
            # 生成随机授权码
            code = ''.join(random.choices(chars, k=length))
            # 检查是否已存在
            if not AuthorizationCode.objects.filter(code=code).exists():
                AuthorizationCode.objects.create(code=code, is_used=False)
                generated_count += 1
        
        self.message_user(request, f'成功生成 {generated_count} 个新授权码')
        return HttpResponseRedirect(reverse('admin:rpi_calculator_authorizationcode_changelist'))
    generate_new_codes.short_description = '生成新授权码'  
    
    # 在顶部添加生成授权码的按钮
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '授权码管理 - 可使用"生成新授权码"操作批量生成'
        return super().changelist_view(request, extra_context)

# 注册RPI用户模型
@admin.register(RPIUser)
class RPIUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'gender', 'age_range', 'relationship_status', 'test_type', 'created_at')
    list_filter = ('gender', 'age_range', 'relationship_status', 'test_type', 'created_at')
    search_fields = ('nickname', 'authorization_code__code')
    ordering = ('-created_at',)
    # 关联授权码
    raw_id_fields = ('authorization_code',)

# 注册RPI测试结果模型
@admin.register(RPITestResult)
class RPITestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_score', 'score_level', 'created_at')
    list_filter = ('score_level', 'created_at')
    search_fields = ('user__nickname',)
    ordering = ('-created_at',)
    # 显示关联的用户信息
    raw_id_fields = ('user',)

# 注册RPI问题模型
@admin.register(RPIQuestion)
class RPIQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_order', 'question_text', 'category')
    list_filter = ('category',)
    search_fields = ('question_text', 'category')
    ordering = ('question_order',)
    # 允许编辑问题顺序
    fields = ('question_order', 'category', 'question_text')

# 注册RPI答案模型
@admin.register(RPIAnswer)
class RPIAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'score', 'answer_text')
    list_filter = ('score',)
    search_fields = ('user__nickname', 'question__question_text')
    ordering = ('user', 'question__question_order')
    # 显示关联的用户和问题
    raw_id_fields = ('user', 'question')
