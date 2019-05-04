from django.urls import path
from . import views


app_name = 'shop'
urlpatterns = [
    path('', views.GoodsListView.as_view(), name='goods_list'),
    path('goods/<int:pk>', views.GoodsDetailView.as_view(), name='goods_detail'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.logout, name='logout'),
]
