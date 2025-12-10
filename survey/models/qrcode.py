# survey/models/qrcode.py
from django.db import models
from django.core.validators import MinValueValidator


class QRCode(models.Model):
    """二维码管理"""
    survey = models.ForeignKey(
        'Survey',
        on_delete=models.CASCADE,
        related_name='qrcodes',
        verbose_name="对应问卷",
        db_index=True
    )
    name = models.CharField(
        max_length=100,
        verbose_name="二维码名称",
        help_text="便于识别的二维码名称"
    )
    short_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="短代码",
        db_index=True,
        help_text="用于生成短链接的唯一代码"
    )
    scan_count = models.IntegerField(
        default=0,
        verbose_name="扫描次数",
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "二维码"
        verbose_name_plural = "二维码"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['short_code']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.survey.title[:20]}"
    
    @property
    def short_url(self):
        """获取短链接（需要根据实际URL配置调整）"""
        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        return f"{base_url}/qr/{self.short_code}"
    
    def increment_scan_count(self):
        """增加扫描次数"""
        self.scan_count = models.F('scan_count') + 1
        self.save(update_fields=['scan_count'])
