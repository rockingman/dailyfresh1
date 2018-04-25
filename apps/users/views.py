import re

from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired

from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
from celery_tasks.tasks import send_active_mail
from dailyfresh import settings
from utils.common import LoginRequiredMixin


class RegisterView(View):
    """类视图：处理注册"""

    def get(self, request):
        """处理GET请求 返回注册页面"""
        return render(request, 'register.html')

    def post(self, request):
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
        user = None
        try:
            user = User.objects.create_user(username, email, password)  # type:User
            # 修改用户状态为未激活
            user.is_active = False
            user.save()
        except IntegrityError:
            # 判断用户是否存在
            # (如果添加的user字段与数据库中的user名字一样就会产生unique约束的冲突 就会报错)
            return render(request, 'register.html', {'errmsg': '用户已存在'})
        # todo: 发送激活邮件
        token = user.generate_active_token()  # 返回字符串类型加密的id
        # 使用celery异步发送不会阻塞
        send_active_mail.delay(username, email, token)
        # 响应请求
        return HttpResponse('进入登录界面！')


class ActiveView(View):
    # tokenredis
    def get(self, request, token: str):
        """
        激活注册用户
        token: 对{'confirm':用户id}字典进行加密后得到的字符串
        :return:
        """
        # 解密数据 得到字典
        dict_data = None
        try:
            # 创建对象                                密钥，          有效时间
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600 * 24)
            # loads接受字节类型 字符串->byes， 返回字典{'confirm':用户id}
            dict_data = s.loads(token.encode())  # 解密的时候报错就表示激活链接失效了
        except SignatureExpired:
            # 激活链接已经过期
            return HttpResponse('激活链接已经过期')
        # 获取用户id
        user_id = dict_data.get('confirm')
        # 激活用户 修改表字段is_active= True
        User.objects.filter(id=user_id).update(is_active=True)
        # 响应请求
        return render(request, 'login.html')


class LoginView(View):
    def get(self, request):
        """进入登录界面"""
        return render(request, 'login.html')

    def post(self, request):
        # 1获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        # 2校验合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '用户和密码不能为空'})
        # 3业务处理
        #  i判断用户名密码正确
        #   使用django自带的用户认证模块实现 authenticate()方法
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码不正确'})
        # ii判断是否激活
        if not user.is_active:
            return render(request, 'login.html', {'errmsg': '用户名未激活'})
        # iii登入用户 使用session保存用户的登录状态
        login(request, user)
        if remember == 'on':
            # 保持登录状态两周（None会保存两周）
            request.session.set_expiry(None)
        else:
            # 关闭浏览器后 登录状态失效
            request.session.set_expiry(0)
        # 4响应请求
        next = request.GET.get('next')
        if next is None:
            return redirect(reverse('goods:index'))
        else:
            return redirect(next)


class Logout(View):
    def get(self, request):
        # 调用django的logout 实现退出 删除session‘键值对数据
        logout(request)
        return redirect(reverse('goods:index'))


class UserAddressView(LoginRequiredMixin, View):
    """用户中心--地址界面"""

    def get(self, request):
        """显示用户地址"""
        try:
            # 查询用户地址 根据创建时间排序 最近的时间在最前 取第一个地址
            # address = Address.objects.filter(user=request.user).order_by('-create_time')[0]
            address = request.user.address_set.latest('create_time')
        except:
            address = None
        data = {
            # 'user': request.user,  #  不需要主动传，django会传
            'address': address,
            'which_page': 3
        }
        return render(request, 'user_center_site.html', data)

    def post(self, request):
        # print("123123")
        # 获取用户请求参数
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')
        # 登录后django用户认证模块默认
        # 会保存user对象到request中 作为request属性
        user = request.user  # 当前登录用户
        # 校验参数合法性
        if not all([receiver, address, mobile]):
            return render(request, 'user_center_site.html', {'errmsg': '参数不完整'})
        # 新增一个地址 保存地址到数据库中
        Address.objects.create(
            receiver_name=receiver,
            receiver_mobile=mobile,
            detail_addr=address,
            zip_code=zip_code,
            user=user
        )
        print(user, "*"*20)
        # 响应请求，刷新当前界面(/users/address)
        return redirect(reverse('users:address'))


class UserOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        data = {'which_page': 2}
        return render(request, 'user_center_order.html', data)


class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取用户对象  如果登录了就会调用login()方法 就能request就会有user属性 也就是User的对象
        user = request.user
        # 查询用户最新添加的地址
        try:
            address = user.address_set.latest('create_time')
        except:
            address = None
        # 从Redis数据库中查询出用户浏览过的商品记录
        # 格式: history_用户id : [商品id1 商品id2 ...]
        # 例:   history_1: [3, 1, 2]
        # 创建strict_redis对象
        strict_redis = get_redis_connection()  # type:strict_redis
        key = 'history_%s' % request.user.id
        # 最多只查看最近浏览过的5条记录
        sku_ids = strict_redis.lrange(key,0,4)  # redis查询语言
        # 获取到的商品id:[3,1,2]
        print(sku_ids)
        # 顺序有问题：根据商品id 查询出商品对象
        # select * from df_goods_sku where id in [3,1,2]
        # skus = GoodsSKU.objects.filter(id__in=sku_ids)
        # 解决：
        skus = []  # 保存查询出来的商品对象
        for sku_id in sku_ids:  #sku_id: bytes
            sku = GoodsSKU.objects.get(id=int(sku_id))
            skus.append(sku)

        # 查询登录用户最近添加的地址 并显示出来
        address = request.user.address_set.latest('create_time')
        context = {
            'which_page': 1,
            'address': address,
            'skus': skus,
        }
        print(context,'-'*20)
        return render(request, 'user_center_info.html', context)
