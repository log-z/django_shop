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
    path('center/member/change_email', views.ChangeMemberEmailView.as_view(), name='change_member_email'),
    path('center/member/change_password', views.ChangeMemberPasswordView.as_view(), name='change_member_password'),

    # 错误页面
    path('error_403', views.error_403_view, name='error_403'),

    # API
    path('api/errors/unauthorized', views.UnauthorizedErrorApiView.as_view(), name='api_unauthorized_error'),
    path('api/errors/internal_server', views.ServerErrorApiView.as_view(), name='api_server_error'),
    path('api/user/email', views.UserEmailAPIView.as_view(), name='api_user_email'),
    path('api/user/password', views.UserPasswordAPIView.as_view(), name='api_user_password'),
]
