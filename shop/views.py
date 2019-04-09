from django.http import HttpResponse
from django.views import  generic

from .models import Goods


def index(request):
    return HttpResponse('shop index page.')


class IndexView(generic.ListView):
    model = Goods
    template_name = 'shop/index.html'
