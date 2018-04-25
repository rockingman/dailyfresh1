from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from apps.users.models import User


class IndexView(View):
    def get(self,request):
        # 显示登录的用户名
        # 方式1：自己主动获取session 查询登录用户并显示
        # user_id = request.session.get('_auth_user_id')
        # user = User.objects.get(id=user_id)
        # context = {'user': user}
        # print(context,111111)
        # return render(request, 'index.html', context)
        # 方式2:使用django用户认证模块
        # user = request.user

        return render(request, 'index.html')