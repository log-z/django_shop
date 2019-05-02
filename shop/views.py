from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.utils import IntegrityError

from .models import User, Goods
from .forms import RegisterFbForm, RegisterBbForm


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


class RegisterView(generic.FormView):
    """用户注册视图"""

    form_class = RegisterFbForm
    template_name = 'shop/register.html'

    def post(self, request, *args, **kwargs):
        form = RegisterFbForm(request.POST)
        username = form['username'].value()
        email = form['email'].value()
        password1 = form['password'].value()
        password2 = form['password_again'].value()

        response_form = RegisterFbForm(dict(username=username, email=email))
        format_error_info = '注册信息格式错误'

        if User.objects.filter(username=username):
            response_form.add_error('username', '该用户已存在')
        elif User.objects.filter(email=email):
            response_form.add_error('email', '该邮箱已被使用')
        elif password1 != password2:
            error_info = '两次输入的密码不一致'
            response_form.add_error('password', error_info)
            response_form.add_error('password_again', error_info)
        elif not RegisterBbForm(request.POST).is_valid():
            for field in response_form.fields:
                response_form.add_error(field, format_error_info)
        else:
            try:
                User(username=username, email=email, password=password1).save()
                return HttpResponse('用户“{}”注册成功'.format(username))
            except IntegrityError:
                for field in response_form.fields:
                    response_form.add_error(field, format_error_info)
        print(response_form.errors)
        return render(request, self.template_name, context={'form': response_form})
