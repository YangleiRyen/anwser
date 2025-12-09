# survey/views.py
import qrcode
import io
import base64
import time
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Survey, Question, Response, Answer, QRCode
from .serializers import SurveySerializer, ResponseSerializer, QRCodeSerializer

class SurveyViewSet(viewsets.ModelViewSet):
    """问卷API"""
    queryset = Survey.objects.filter(is_active=True)
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = Survey.objects.filter(is_active=True)
        
        # 时间过滤
        now = datetime.now()
        queryset = queryset.filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now),
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交问卷"""
        survey = self.get_object()
        
        # 检查是否允许提交
        if not self._can_submit(survey, request):
            return Response(
                {'error': '无法提交问卷'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ResponseSerializer(data=request.data)
        if serializer.is_valid():
            # 添加额外信息
            response_data = serializer.validated_data
            response_data['survey'] = survey
            response_data['ip_address'] = self._get_client_ip(request)
            response_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            
            # 如果有用户登录，关联用户
            if request.user.is_authenticated:
                response_data['respondent'] = request.user
            
            response = serializer.save()
            
            # 生成微信扫码记录
            if 'wechat_openid' in request.data:
                self._record_wechat_info(response, request.data)
            
            return Response({
                'success': True,
                'message': '问卷提交成功',
                'response_id': str(response.id)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _can_submit(self, survey, request):
        """检查是否可以提交问卷"""
        # 检查时间
        now = datetime.now()
        if survey.start_date and survey.start_date > now:
            return False
        if survey.end_date and survey.end_date < now:
            return False
        
        # 检查微信要求
        if survey.require_wechat:
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            if 'micromessenger' not in user_agent:
                return False
        
        # 检查提交限制
        if survey.limit_per_user > 0:
            if request.user.is_authenticated:
                count = Response.objects.filter(
                    survey=survey,
                    respondent=request.user
                ).count()
                if count >= survey.limit_per_user:
                    return False
            else:
                # 匿名用户检查session
                session_key = request.session.session_key
                if session_key:
                    count = Response.objects.filter(
                        survey=survey,
                        session_key=session_key
                    ).count()
                    if count >= survey.limit_per_user:
                        return False
        
        return True
    
    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _record_wechat_info(self, response, data):
        """记录微信信息"""
        response.wechat_openid = data.get('wechat_openid', '')
        response.wechat_unionid = data.get('wechat_unionid', '')
        response.wechat_nickname = data.get('wechat_nickname', '')
        response.save()

class QRCodeViewSet(viewsets.ModelViewSet):
    """二维码API"""
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """创建问卷二维码"""
        survey_id = request.data.get('survey_id')
        name = request.data.get('name', '问卷二维码')
        
        survey = get_object_or_404(Survey, id=survey_id)
        
        # 生成短代码
        import random
        import string
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        qrcode_obj = QRCode.objects.create(
            survey=survey,
            name=name,
            short_code=short_code
        )
        
        serializer = self.get_serializer(qrcode_obj)
        return Response(serializer.data)

# 前端页面视图
class SurveyDetailView(DetailView):
    """问卷详情页"""
    model = Survey
    template_name = 'survey/detail.html'
    context_object_name = 'survey'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 检查是否微信浏览器
        user_agent = self.request.META.get('HTTP_USER_AGENT', '').lower()
        context['is_wechat'] = 'micromessenger' in user_agent
        
        # 记录访问开始时间（用于计算填写时长）
        self.request.session[f'survey_start_{self.object.id}'] = timezone.now().timestamp()
        
        # 从中间表获取问卷的问题
        survey_questions = self.object.survey_questions.all().order_by('order')
        
        # 确保问题被正确序列化
        context['questions'] = survey_questions
        
        # 获取问卷中所有的分类（去重）
        categories = []
        category_ids = set()
        for sq in survey_questions:
            category = sq.category
            if category and category.id not in category_ids:
                category_ids.add(category.id)
                categories.append(category)
        context['categories'] = categories
        
        # 添加调试信息
        if self.request.GET.get('debug'):
            context['debug'] = True
            context['questions_count'] = survey_questions.count()
            context['questions_list'] = list(survey_questions.values('id', 'question__text', 'question__question_type'))
            context['categories_list'] = list(categories)
        
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # 检查问卷是否有效
        now = timezone.now()
        if self.object.start_date and self.object.start_date > now:
            return render(request, 'survey/not_started.html', {
                'survey': self.object,
                'start_time': self.object.start_date
            })
        
        if self.object.end_date and self.object.end_date < now:
            return render(request, 'survey/ended.html', {
                'survey': self.object,
                'end_time': self.object.end_date
            })
        
        if not self.object.is_active:
            return render(request, 'survey/inactive.html', {
                'survey': self.object
            })
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

# survey/views.py - 更新 QRCodeRedirectView
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

class SubmitSurveyView(View):
    """提交问卷（处理微信数据）"""
    
    def post(self, request, survey_id):
        survey = get_object_or_404(Survey, id=survey_id)
        
        # 验证数据
        data = request.POST.copy()
        
        # 计算完成时间
        start_time = request.session.get(f'survey_start_{survey_id}')
        if start_time:
            completion_time = int(time.time() - start_time)
            data['completion_time'] = completion_time
        
        # 添加微信信息
        if self._is_wechat_browser(request):
            wechat_info = request.session.get('wechat_user_info', {})
            data.update({
                'wechat_openid': wechat_info.get('openid', ''),
                'wechat_nickname': wechat_info.get('nickname', '')
            })
        
        # 保存回答
        response = Response.objects.create(
            survey=survey,
            session_key=request.session.session_key,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            wechat_openid=data.get('wechat_openid', ''),
            wechat_nickname=data.get('wechat_nickname', ''),
            completion_time=data.get('completion_time', 0)
        )
        
        # 保存每个问题的答案
        for survey_question in survey.survey_questions.all():
            question = survey_question.question
            answer_key = f'question_{survey_question.id}'
            if answer_key in data:
                Answer.objects.create(
                    response=response,
                    question=question,
                    answer_text=data[answer_key] if question.question_type == 'text' else '',
                    answer_choice=[data[answer_key]] if question.question_type in ['single_choice', 'rating'] else data.getlist(answer_key)
                )
        
        # 清除session中的开始时间
        if f'survey_start_{survey_id}' in request.session:
            del request.session[f'survey_start_{survey_id}']
        
        return JsonResponse({
            'success': True,
            'message': '提交成功',
            'response_id': str(response.id)
        })
    
    def _is_wechat_browser(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        return 'micromessenger' in user_agent
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# 微信相关视图
class WeChatAuthView(View):
    """微信授权（如果需要获取用户信息）"""
    
    def get(self, request):
        # 微信授权逻辑
        # 这里需要配置微信开放平台
        app_id = settings.WECHAT_APP_ID
        redirect_uri = request.build_absolute_uri('/wechat/callback/')
        
        auth_url = (
            f"https://open.weixin.qq.com/connect/oauth2/authorize"
            f"?appid={app_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=snsapi_userinfo"
            f"&state={request.GET.get('next', '/')}"
            f"#wechat_redirect"
        )
        
        return redirect(auth_url)

class WeChatCallbackView(View):
    """微信授权回调"""
    
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state', '/')
        
        if not code:
            return redirect('/')
        
        # 获取access_token
        app_id = settings.WECHAT_APP_ID
        app_secret = settings.WECHAT_APP_SECRET
        
        import requests
        
        # 获取access_token
        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        token_params = {
            'appid': app_id,
            'secret': app_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.get(token_url, params=token_params)
        token_data = response.json()
        
        if 'access_token' in token_data:
            # 获取用户信息
            user_info_url = "https://api.weixin.qq.com/sns/userinfo"
            user_params = {
                'access_token': token_data['access_token'],
                'openid': token_data['openid'],
                'lang': 'zh_CN'
            }
            
            user_response = requests.get(user_info_url, params=user_params)
            user_data = user_response.json()
            
            # 保存到session
            request.session['wechat_user_info'] = {
                'openid': user_data.get('openid'),
                'nickname': user_data.get('nickname'),
                'headimgurl': user_data.get('headimgurl'),
                'unionid': user_data.get('unionid', '')
            }
        
        return redirect(state)

@api_view(['GET'])
def survey_statistics(request, survey_id):
    """获取问卷统计"""
    survey = get_object_or_404(Survey, id=survey_id)
    
    # 基本统计
    total_responses = survey.responses.count()
    
    # 问题统计
    question_stats = []
    for survey_question in survey.survey_questions.all():
        question = survey_question.question
        answers = Answer.objects.filter(question=question)
        
        stats = {
            'question_id': str(question.id),
            'question_text': question.text,
            'question_type': question.question_type,
            'total_answers': answers.count(),
        }
        
        if question.question_type in ['single_choice', 'multiple_choice']:
            # 选项统计
            option_counts = {}
            for answer in answers:
                for choice in answer.answer_choice:
                    option_counts[choice] = option_counts.get(choice, 0) + 1
            
            stats['options'] = option_counts
        
        question_stats.append(stats)
    
    return Response({
        'survey': {
            'title': survey.title,
            'total_responses': total_responses
        },
        'question_stats': question_stats
    })