from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    """检测用户是否已经登录"""
    @classmethod
    def as_view(cls):
        # super():MRO搜索的下一个类
        # 会调用View的as_view方法 并返回视图函数
        view_fun = super().as_view()
        # 对视图函数进行装饰
        view_fun = login_required(view_fun)
        # 返回装饰后的视图函数
        return view_fun