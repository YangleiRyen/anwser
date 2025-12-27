from django.urls import path
from .views import RPILandingView, RPIAuthView, RPIQuestionView, RPIResultView

app_name = 'rpi_calculator'

urlpatterns = [
    # RPI计算器首页
    path('', RPILandingView.as_view(), name='rpi_landing'),
    # 授权码验证页面
    path('auth/', RPIAuthView.as_view(), name='rpi_auth'),
    # 测试问题页面
    path('question/', RPIQuestionView.as_view(), name='rpi_question'),
    # 测试结果页面
    path('result/', RPIResultView.as_view(), name='rpi_result'),
]
