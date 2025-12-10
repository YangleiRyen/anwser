# survey/admin/qrcode_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
import random
import string
import uuid

from ..models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    """二维码管理"""
    list_display = ['name', 'survey', 'short_code', 'scan_count', 'created_at', 'qr_code_preview']
    list_filter = ['survey', 'created_at']
    search_fields = ['name', 'short_code', 'survey__title']
    readonly_fields = ['scan_count', 'created_at', 'qr_code_preview', 'download_qrcode']
    list_select_related = ['survey']
    
    fieldsets = (
        (None, {
            'fields': ('survey', 'name', 'short_code')
        }),
        ('统计信息', {
            'fields': ('scan_count', 'created_at'),
            'classes': ('collapse',)
        }),
        ('二维码', {
            'fields': ('qr_code_preview', 'download_qrcode'),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """处理GET参数，自动填充survey字段"""
        form = super().get_form(request, obj, **kwargs)
        survey_id = request.GET.get('survey')
        if survey_id and not obj:
            try:
                from ..models import Survey
                Survey.objects.get(pk=survey_id)  # 验证survey存在
                form.base_fields['survey'].initial = survey_id
                form.base_fields['survey'].widget.attrs['readonly'] = True
                form.base_fields['survey'].disabled = True
            except Exception:
                pass
        return form
    
    def save_model(self, request, obj, form, change):
        """保存模型时自动生成短代码"""
        if not change and request.GET.get('survey'):
            try:
                from ..models import Survey
                survey = Survey.objects.get(pk=request.GET.get('survey'))
                obj.survey = survey
            except Survey.DoesNotExist:
                pass
        
        # 生成唯一的短代码
        if not obj.short_code:
            obj.short_code = self._generate_unique_short_code()
        
        super().save_model(request, obj, form, change)
    
    def _generate_unique_short_code(self, length=8):
        """生成唯一的短代码"""
        max_attempts = 10
        for _ in range(max_attempts):
            code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
            if not QRCode.objects.filter(short_code=code).exists():
                return code
        # 如果多次尝试失败，使用UUID
        return str(uuid.uuid4())[:8]
    
    def qr_code_preview(self, obj):
        """二维码预览"""
        if not obj.short_code:
            return '请先保存生成二维码'
        
        return format_html('''
            <div style="margin: 10px 0;">
                <strong>二维码预览：</strong><br>
                <img src="/qrcode/{}/image/" alt="二维码" style="width: 200px; height: 200px; margin: 10px 0; border: 1px solid #ddd; padding: 5px;"><br>
                <a href="/qrcode/{}/image/" target="_blank" style="margin-right: 10px;">查看大图</a>
            </div>
        ''', obj.short_code, obj.short_code)
    qr_code_preview.short_description = '二维码预览'
    
    def download_qrcode(self, obj):
        """下载二维码"""
        if not obj.short_code:
            return ''
        
        return format_html('''
            <div style="margin: 10px 0;">
                <a href="/qrcode/{}/image/" download="qrcode_{}_{}.png" class="button" style="background-color: #4CAF50; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">
                    📥 下载二维码
                </a>
            </div>
        ''', obj.short_code, obj.short_code, obj.name)
    download_qrcode.short_description = '下载'
