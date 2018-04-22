from django.conf.urls import url

from apps.users import views

urlpatterns = [
    # url(r'^register$',views.register,name='register'),
    # url(r'^do_register$',views.do_register,name='do_register'),
    # 类视图：as_view() 返回一个视图函数 注意：要添加括号!!! as_view返回一个view
    url(r'^register$',views.RegisterView.as_view(),name='register'),
    url(r'^active/(.+)$',views.ActiveView.as_view(),name='active')
]
