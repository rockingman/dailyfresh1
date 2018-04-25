from django.conf.urls import url

from apps.goods import views

urlpatterns = [
    # :8000/index 首页
    url(r'^index$',views.IndexView.as_view(),name='index'),

]
