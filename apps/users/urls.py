from django.conf.urls import url

from apps.users import views

urlpatterns = [
    # 类视图：as_view() 返回一个视图函数 注意：要添加括号!!! as_view返回一个view
    url(r'^register$',views.RegisterView.as_view(),name='register'),
    # 127.0.0.1:8000/users/login 登录页面
    url(r'^login$',views.LoginView.as_view(),name='login'),
    url(r'^active/(.+)$',views.ActiveView.as_view(),name='active'),
    # :8000/users/logout
    url(r'^logout$',views.Logout.as_view(),name='logout'),
    # :8000/users/address
    url(r'^address$',views.UserAddressView.as_view(),name='address'),
    url(r'^orders$',views.UserOrdersView.as_view(),name='orders'),
    url(r'^$',views.UserInfoView.as_view(),name='info'),

]
