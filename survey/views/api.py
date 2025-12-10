# survey/views/api.py
import time
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from ..models import Survey, Question, Response, Answer, QRCode
from ..serializers import SurveySerializer, ResponseSerializer, QRCodeSerializer

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
