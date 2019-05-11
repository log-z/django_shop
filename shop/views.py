from django.views import generic
from django.shortcuts import reverse, get_object_or_404, HttpResponseRedirect
from django.db.utils import IntegrityError

from .models import User, Goods
from .forms import RegisterFbForm, RegisterBbForm, LoginFbForm


def get_current_user(request):
    """获取当前用户对象"""

    try:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)
        return user
    except (User.DoesNotExist, KeyError):
        return None


def redirect_to_index():
    """重定向到首页"""

    return HttpResponseRedirect(reverse('shop:goods_list'))


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

        # 添加当前用户context
        object_list['current_user'] = get_current_user(self.request)

        return object_list


class GoodsDetailView(generic.DetailView):
    """商品详情视图"""

    model = Goods
    template_name = 'shop/goods_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = super().get_context_data(**kwargs)

        # 添加商家到context
        object_list['seller'] = self.object.seller
        # 添加当前用户context
        object_list['current_user'] = get_current_user(self.request)

        return object_list


class RegisterView(generic.FormView):
    """用户注册视图"""

    form_class = RegisterFbForm
    template_name = 'shop/register.html'

    def get(self, request, *args, **kwargs):
        if request.session.get('user_id', None):
            return redirect_to_index()
        else:
            return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        if request.session.get('user_id', None):
            return redirect_to_index()

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
                user = User(username=username, email=email, password=password1)
                user.save()
                request.session['user_id'] = user.id

                return redirect_to_index()
            except IntegrityError:
                for field in response_form.fields:
                    response_form.add_error(field, format_error_info)

        return self.form_invalid(response_form)


class LoginView(generic.FormView):
    """用户登陆视图"""

    form_class = LoginFbForm
    template_name = 'shop/login.html'

    def get(self, request, *args, **kwargs):
        if request.session.get('user_id', None):
            return redirect_to_index()
        else:
            return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        if request.session.get('user_id', None):
            return redirect_to_index()

        form = LoginFbForm(request.POST)
        username = form['username'].value()
        password = form['password'].value()

        response_form = LoginFbForm(dict(username='', email=''))
        error_info = '账号或密码错误'

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise User.DoesNotExist()

            request.session['user_id'] = user.id
        except User.DoesNotExist:
            response_form.add_error('username', error_info)
            response_form.add_error('password', error_info)

            return self.form_invalid(response_form)
        else:
            return redirect_to_index()


def logout(request):
    """退出用户登陆"""

    del request.session['user_id']
    return HttpResponseRedirect(reverse('shop:login'))
