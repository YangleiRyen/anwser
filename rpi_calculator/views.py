from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.views.generic import View, TemplateView
from .models import AuthorizationCode, RPIUser, RPITestResult, RPIQuestion, RPIAnswer

class RPILandingView(TemplateView):
    """RPI计算器首页"""
    template_name = 'rpi_calculator/landing.html'

class RPIAuthView(View):
    """RPI测试授权码验证视图"""
    def get(self, request):
        return render(request, 'rpi_calculator/auth.html')
    
    def post(self, request):
        code = request.POST.get('code', '').strip().upper()
        if not code:
            return render(request, 'rpi_calculator/auth.html', {'error': '请输入授权码'})
        
        try:
            # 不区分大小写查询授权码
            auth_code = AuthorizationCode.objects.get(code__iexact=code, is_used=False)
            # 将授权码标记为已使用
            auth_code.is_used = True
            auth_code.save()
            # 创建RPI用户
            rpi_user = RPIUser.objects.create(authorization_code=auth_code)
            # 将用户ID存储在会话中
            request.session['rpi_user_id'] = rpi_user.id
            return redirect('rpi_calculator:rpi_question')
        except AuthorizationCode.DoesNotExist:
            # 检查是否存在但已使用的授权码
            if AuthorizationCode.objects.filter(code__iexact=code, is_used=True).exists():
                return render(request, 'rpi_calculator/auth.html', {'error': '该授权码已被使用'})
            return render(request, 'rpi_calculator/auth.html', {'error': '无效的授权码'})
        except Exception as e:
            return render(request, 'rpi_calculator/auth.html', {'error': f'验证失败：{str(e)}'})

class RPIQuestionView(View):
    """RPI测试问题视图"""
    def get(self, request):
        # 检查会话中是否有用户ID
        rpi_user_id = request.session.get('rpi_user_id')
        if not rpi_user_id:
            return redirect('rpi_calculator:rpi_auth')
        
        # 获取用户
        rpi_user = get_object_or_404(RPIUser, id=rpi_user_id)
        
        # 获取所有问题
        questions = RPIQuestion.objects.all()
        
        # 渲染问题页面
        return render(request, 'rpi_calculator/question.html', {
            'questions': questions,
            'user': rpi_user
        })
    
    def post(self, request):
        # 检查会话中是否有用户ID
        rpi_user_id = request.session.get('rpi_user_id')
        if not rpi_user_id:
            return redirect('rpi_calculator:rpi_auth')
        
        # 获取用户
        rpi_user = get_object_or_404(RPIUser, id=rpi_user_id)
        
        # 处理问题答案
        total_score = 0
        questions = RPIQuestion.objects.all()
        
        for question in questions:
            score = request.POST.get(f'question_{question.id}', None)
            if score is None:
                return HttpResponseBadRequest('请回答所有问题')
            
            score = int(score)
            total_score += score
            
            # 创建答案记录
            RPIAnswer.objects.create(
                user=rpi_user,
                question=question,
                score=score,
                answer_text=f'得分：{score}'
            )
        
        # 计算得分等级和结果
        score_level = self._get_score_level(total_score)
        summary = self._get_summary(score_level)
        detailed_analysis = self._get_detailed_analysis(score_level)
        suggestions = self._get_suggestions(score_level)
        
        # 创建测试结果
        RPITestResult.objects.create(
            user=rpi_user,
            total_score=total_score,
            score_level=score_level,
            summary=summary,
            detailed_analysis=detailed_analysis,
            suggestions=suggestions
        )
        
        return redirect('rpi_calculator:rpi_result')
    
    def _get_score_level(self, total_score):
        """根据总分获取得分等级"""
        if total_score < 30:
            return 'low'
        elif total_score < 60:
            return 'medium'
        else:
            return 'high'
    
    def _get_summary(self, score_level):
        """根据得分等级获取结果总结"""
        summaries = {
            'low': '您的关系占有欲指数较低，表现为对伴侣的信任度较高，给予对方充分的个人空间。',
            'medium': '您的关系占有欲指数适中，既能表达对伴侣的关心，又能保持适当的距离。',
            'high': '您的关系占有欲指数较高，需要注意不要过度干涉伴侣的生活，给予对方足够的自由。'
        }
        return summaries.get(score_level, '')
    
    def _get_detailed_analysis(self, score_level):
        """根据得分等级获取详细分析"""
        analyses = {
            'low': '您在关系中表现出较高的安全感和信任度，不会轻易怀疑伴侣。您尊重对方的个人边界，鼓励对方发展自己的兴趣爱好和社交圈。这种态度有助于维持健康、平等的伴侣关系。',
            'medium': '您在关系中保持着良好的平衡，既能表达对伴侣的关心和在意，又能理解对方需要个人空间。您会适度参与伴侣的生活，但不会过度干涉。这种态度有助于建立稳定、和谐的伴侣关系。',
            'high': '您在关系中可能表现出较强的控制欲和占有欲，容易对伴侣的行为产生怀疑。您可能过度关注伴侣的行踪和社交圈，甚至限制对方的自由。这种态度可能会给伴侣带来压力，影响关系的健康发展。'
        }
        return analyses.get(score_level, '')
    
    def _get_suggestions(self, score_level):
        """根据得分等级获取建议"""
        suggestions = {
            'low': '继续保持这种信任和尊重的态度。但也要注意不要过度忽视伴侣的情感需求，适时表达关心和在意。',
            'medium': '继续维持这种平衡的态度。在表达关心的同时，注意倾听伴侣的想法和感受，共同维护健康的伴侣关系。',
            'high': '建议您反思自己的行为模式，尝试给予伴侣更多的信任和自由。学会尊重对方的个人边界，培养自己的兴趣爱好和社交圈，减少对伴侣的过度依赖。如果情况严重，建议寻求专业心理咨询帮助。'
        }
        return suggestions.get(score_level, '')

class RPIResultView(View):
    """RPI测试结果视图"""
    def get(self, request):
        # 检查会话中是否有用户ID
        rpi_user_id = request.session.get('rpi_user_id')
        if not rpi_user_id:
            return redirect('rpi_calculator:rpi_auth')
        
        # 获取用户和测试结果
        rpi_user = get_object_or_404(RPIUser, id=rpi_user_id)
        test_result = get_object_or_404(RPITestResult, user=rpi_user)
        
        # 渲染结果页面
        return render(request, 'rpi_calculator/result.html', {
            'user': rpi_user,
            'result': test_result
        })
    
    def post(self, request):
        # 清除会话信息，返回首页
        request.session.pop('rpi_user_id', None)
        return redirect('rpi_calculator:rpi_landing')

