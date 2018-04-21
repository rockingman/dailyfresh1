import re
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render
# Create your views here.
from django.views.generic.base import View
from apps.users.models import User
class RegisterView(View):
    """类视图：处理注册"""
    def get(self,request):
        """处理GET请求 返回注册页面"""
        return render(request,'register.html')
    def post(self,request):
        """处理POST请求 返回注册逻辑"""
        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # todo: 校验参数合法性
        # 判断参数不能为空
        if not all([username, password, password2, email]):
            return render(request, 'register.html', {'errmsg': '参数不完整'})
        # 判断两次输入的密码一致
        if password != password2:
            return render(request, 'register.html', {'errmsg': '两次输入的密码不一致'})
        # 判断邮箱合法
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})
        # 判断是否勾选用户协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选用户协议'})
        # 处理业务：保存用户到数据表中
        try:
            user = User.objects.create_user(username, email, password)
            # 修改用户状态为未激活
            user.is_active = False
            user.save()
        except IntegrityError:
            # 判断用户是否存在
            # (如果添加的user字段与数据库中的user名字一样就会产生unique约束的冲突 就会报错)
            return render(request, 'register.html', {'errmsg': '用户已存在'})

        # todo: 发送激活邮件
        # 响应请求
        return HttpResponse('注册成功！')

# def register(request):
#     """进入注册界面"""
#     return render(request,'register.html')
#
# def do_register(request):
#     """实现注册功能"""
#     # 获取post请求参数
#     username=request.POST.get('username')
#     password=request.POST.get('password')
#     password2=request.POST.get('password2')
#     email=request.POST.get('email')
#     allow=request.POST.get('allow')
#     # todo: 校验参数合法性
#     # 判断参数不能为空
#     if not all([username,password,password2,email]):
#         return render(request,'register.html',{'errmsg':'参数不完整'})
#     # 判断两次输入的密码一致
#     if password != password2:
#         return render(request,'register.html',{'errmsg':'两次输入的密码不一致'})
#     # 判断邮箱合法
#     if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
#         return render(request,'register.html',{'errmsg':'邮箱不合法'})
#     # 判断是否勾选用户协议
#     if allow != 'on':
#         return render(request,'register.html',{'errmsg':'请勾选用户协议'})
#     # 处理业务：保存用户到数据表中
#     try:
#         user=User.objects.create_user(username,email,password)
#         # 修改用户状态为未激活
#         user.is_active= False
#         user.save()
#     except IntegrityError:
#         # 判断用户是否存在
#         return render(request,'register.html',{'errmsg':'用户已存在'})
#
#     # 判断用户是否存在
#
#
#     # todo: 发送激活邮件
#
#     # 响应请求
#     return HttpResponse('注册成功！')