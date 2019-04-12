from django.views import generic

from .models import Goods


class GoodsListView(generic.ListView):
    """商品列表视图"""

    model = Goods
    template_name = 'shop/goods_list.html'
