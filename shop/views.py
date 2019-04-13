from django.views import generic
from django.shortcuts import get_object_or_404

from .models import User, Goods


class GoodsListView(generic.ListView):
    """商品列表视图"""

    template_name = 'shop/goods_list.html'

    def get_queryset(self):
        queryset = Goods.objects.all()

        # 按商品关键词过滤
        if 'g' in self.request.GET:
            goods_kws = self.request.GET['g']
            queryset = queryset.filter(goods_name__contains=goods_kws)

        # 按商家ID过滤
        if 's' in self.request.GET:
            seller_id = self.request.GET['s']
            queryset = queryset.filter(seller_id=seller_id)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = super().get_context_data(**kwargs)

        # 添加搜索词到context
        if 'g' in self.request.GET:
            object_list['search_text'] = self.request.GET['g']

        # 添加商家到context
        if 's' in self.request.GET:
            object_list['seller'] = get_object_or_404(User, id=self.request.GET['s'])

        return object_list


class GoodsDetailView(generic.DetailView):
    """商品详情视图"""

    model = Goods
    template_name = 'shop/goods_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = super().get_context_data(**kwargs)

        # 添加商家到context
        object_list['seller'] = self.object.seller
        return object_list
