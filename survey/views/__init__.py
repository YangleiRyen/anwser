# survey/views/__init__.py
# 导入所有视图类和函数，方便统一引用
from .api import SurveyViewSet, QRCodeViewSet, survey_statistics
from .survey import SurveyDetailView, SubmitSurveyView
from .qrcode import QRCodeRedirectView, QRCodeImageView
from .wechat import WeChatAuthView, WeChatCallbackView
