# survey/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'surveys', views.SurveyViewSet)
router.register(r'qrcodes', views.QRCodeViewSet)

urlpatterns = [
    # API路由
    path('api/', include(router.urls)),
    
    # 问卷页面
    path('survey/<uuid:pk>/', views.SurveyDetailView.as_view(), name='survey-detail'),
    path('survey/<uuid:survey_id>/submit/', views.SubmitSurveyView.as_view(), name='submit-survey'),
    
    # 二维码相关
    path('qrcode/<str:short_code>/redirect/', views.QRCodeRedirectView.as_view(), name='qrcode-redirect'),
    path('qrcode/<str:short_code>/image/', views.QRCodeImageView.as_view(), name='qrcode-image'),
    
    # 微信相关
    path('wechat/auth/', views.WeChatAuthView.as_view(), name='wechat-auth'),
    path('wechat/callback/', views.WeChatCallbackView.as_view(), name='wechat-callback'),
    
    # 统计
    path('api/survey/<uuid:survey_id>/stats/', views.survey_statistics, name='survey-stats'),
]