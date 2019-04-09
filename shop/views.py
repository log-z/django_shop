from django.http import HttpResponse


def index(request):
    return HttpResponse('shop index page.')
