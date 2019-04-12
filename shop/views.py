from django.views import generic

from .models import Goods


class GoodsListView(generic.ListView):
    """商品列表视图"""

    template_name = 'shop/goods_list.html'

    def get_queryset(self):
        queryset = Goods.objects.all()

        if 'g' in self.request.GET:
            goods_kws = self.request.GET['g']
            queryset = queryset.filter(goods_name__contains=goods_kws)

        if 's' in self.request.GET:
            seller_id = self.request.GET['s']
            queryset = queryset.filter(seller_id=seller_id)

        return queryset


class GoodsDetailView(generic.DetailView):
    """商品详情视图"""

    model = Goods
    template_name = 'shop/goods_detail.html'
