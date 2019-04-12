from django.urls import path
from . import views


app_name = 'shop'
urlpatterns = [
    path('', views.GoodsListView.as_view(), name='goods_list'),
    path('goods/<int:pk>', views.GoodsDetailView.as_view(), name='goods_detail'),
]
