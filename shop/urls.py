from django.urls import path
from . import views


app_name = 'shop'
urlpatterns = [
    # 浏览商品
    path('', views.GoodsListView.as_view(), name='goods_list'),
    path('goods/<int:pk>', views.GoodsDetailView.as_view(), name='goods_detail'),

    # 用户登陆注册
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),

    # 用户中心
    path('center', views.center_enter_view, name='center'),
    path('center/member', views.MemberInfoView.as_view(), name='member_info'),
    path('error_403', views.error_403_view, name='error_403'),
]
