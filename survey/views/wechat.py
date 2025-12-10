# survey/views/wechat.py
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.conf import settings

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
