# survey/views/survey.py
import time
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.views.generic import DetailView
from django.utils import timezone
from ..models import Survey, Question, Response, Answer

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
