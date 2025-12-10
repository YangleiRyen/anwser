# survey/views/qrcode.py
import qrcode
import io
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from ..models import QRCode, Survey

class QRCodeRedirectView(View):
    """二维码跳转视图"""
    
    def get(self, request, short_code):
        qrcode_obj = get_object_or_404(QRCode, short_code=short_code)
        
        # 增加扫描计数
        qrcode_obj.scan_count += 1
        qrcode_obj.save()
        
        # 检查问卷是否要求必须在微信中打开
        if qrcode_obj.survey.require_wechat:
            # 检查微信环境
            is_wechat = self._is_wechat_browser(request)
            
            if is_wechat:
                # 微信内直接跳转到问卷
                return redirect('survey-detail', pk=str(qrcode_obj.survey.id))
            else:
                # 非微信环境显示提示页面
                return render(request, 'survey/wechat_required.html', {
                    'survey': qrcode_obj.survey,
                    'qrcode': qrcode_obj,
                    'redirect_url': request.build_absolute_uri(
                        f'/survey/{qrcode_obj.survey.id}/'
                    )
                })
        else:
            # 问卷不要求必须在微信中打开，直接跳转到问卷
            return redirect('survey-detail', pk=str(qrcode_obj.survey.id))
    
    def _is_wechat_browser(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        return 'micromessenger' in user_agent

class QRCodeImageView(View):
    """生成二维码图片，支持自定义样式"""
    
    def get(self, request, short_code):
        qrcode_obj = get_object_or_404(QRCode, short_code=short_code)
        
        # 构建问卷URL
        survey_url = request.build_absolute_uri(
            f'/qrcode/{short_code}/redirect/'
        )
        
        # 获取样式参数
        version = int(request.GET.get('version', 1))
        error_correction = request.GET.get('error_correction', 'L')
        box_size = int(request.GET.get('box_size', 10))
        border = int(request.GET.get('border', 4))
        fill_color = request.GET.get('fill_color', 'black')
        back_color = request.GET.get('back_color', 'white')
        
        # 映射纠错级别
        error_correction_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction_map.get(error_correction, qrcode.constants.ERROR_CORRECT_L),
            box_size=box_size,
            border=border,
        )
        qr.add_data(survey_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # 保存到响应
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        
        return HttpResponse(buffer.getvalue(), content_type="image/png")
