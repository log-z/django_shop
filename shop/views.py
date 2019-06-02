from django.views import generic
from django.shortcuts import reverse, get_object_or_404, HttpResponseRedirect
from django.db.utils import IntegrityError

from .models import User, Goods
from .forms import RegisterFEForm, RegisterBEForm, LoginFEForm, LoginBEForm


def get_current_user(request):
    """获取当前用户对象"""

    try:
        user_id = request.session['user_id']
        user = User.objects.get(id=user_id)

        return user
    except (User.DoesNotExist, KeyError) as e:
        # 删除无效的用户登陆关联
        if type(e) is User.DoesNotExist:
            associate_user_to_client(request, None)

        return None


def associate_user_to_client(request, user_id):
    """关联用户登陆到客户端"""

    if user_id is None:
        request.session.flush()
    else:
        request.session['user_id'] = user_id


def redirect_to_index():
    """重定向到首页"""

    return HttpResponseRedirect(reverse('shop:goods_list'))


class BasicUserView(generic.base.ContextMixin):
    """可提供用户信息的基本视图

    是所有需要使用用户信息的视图的基类。
    这并不是个直接可用的视图（至少目前是这样）。
    """

    def get_context_data(self, **kwargs):
        request = kwargs.pop('request')
        object_list = {
            # 添加当前用户context
            'current_user': get_current_user(request),
        }

        kwargs.update(object_list)
        return super().get_context_data(**kwargs)


class GoodsListView(generic.ListView, BasicUserView):
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
        object_list = super().get_context_data(request=self.request, kwargs=kwargs)

        # 添加搜索词到context
        if 'g' in self.request.GET:
            object_list['search_text'] = self.request.GET['g']

        # 添加商家到context
        if 's' in self.request.GET:
            object_list['seller'] = get_object_or_404(User, id=self.request.GET['s'])

        return object_list


class GoodsDetailView(generic.DetailView, BasicUserView):
    """商品详情视图"""

    model = Goods
    template_name = 'shop/goods_detail.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        object_list = super().get_context_data(request=self.request, **kwargs)

        # 添加商家到context
        object_list['seller'] = self.object.seller

        return object_list


class RegisterView(generic.FormView):
    """用户注册视图"""

    form_class = RegisterFEForm
    template_name = 'shop/register.html'

    def get(self, request, *args, **kwargs):
        if get_current_user(request) is not None:
            return redirect_to_index()
        else:
            return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        if get_current_user(request) is not None:
            return redirect_to_index()

        request_form = RegisterFEForm(request.POST)
        username = request_form['username'].value()
        email = request_form['email'].value()
        password1 = request_form['password'].value()
        password2 = request_form['password_again'].value()

        response_form = RegisterFEForm(dict(username=username, email=email))
        format_error_info = '注册信息格式错误'

        if not RegisterBEForm(request.POST).is_valid():
            # 表单格式错误
            for field in response_form.fields:
                response_form.add_error(field, format_error_info)
        elif User.objects.filter(username=username):
            # 该用户名已被使用
            response_form.add_error('username', '该用户名已被使用')
        elif User.objects.filter(email=email):
            # 该邮箱已被使用
            response_form.add_error('email', '该邮箱已被使用')
        elif password1 != password2:
            # 两次输入的密码不一致
            error_info = '两次输入的密码不一致'
            response_form.add_error('password', error_info)
            response_form.add_error('password_again', error_info)
        else:
            # 尝试新增用户
            try:
                user = User(username=username, email=email, password=password1)
                user.save()
                associate_user_to_client(request, user.id)

                return redirect_to_index()
            except IntegrityError:
                # 新增用户到数据库失败
                for field in response_form.fields:
                    response_form.add_error(field, format_error_info)

        return self.form_invalid(response_form)


class LoginView(generic.FormView):
    """用户登陆视图"""

    form_class = LoginFEForm
    template_name = 'shop/login.html'

    def get(self, request, *args, **kwargs):
        if get_current_user(request) is not None:
            return redirect_to_index()
        else:
            return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        if get_current_user(request) is not None:
            return redirect_to_index()

        request_form = LoginFEForm(request.POST)
        username = request_form['username'].value()
        password = request_form['password'].value()

        response_form = LoginFEForm(dict(username='', email=''))

        if not LoginBEForm(request.POST).is_valid():
            # 表单格式错误
            for field in response_form.fields:
                response_form.add_error(field, '注册信息格式错误')
        else:
            # 尝试登陆，检查用户名和密码
            try:
                user = User.objects.get(username=username)
                if not user.check_password(password):
                    raise User.DoesNotExist()

                associate_user_to_client(request, user.id)

                # 登陆成功
                return redirect_to_index()
            except User.DoesNotExist:
                # 用户名或密码错误
                error_info = '用户名或密码错误'
                response_form.add_error('username', error_info)
                response_form.add_error('password', error_info)

        return self.form_invalid(response_form)


def logout_view(request):
    """退出用户登陆视图"""

    associate_user_to_client(request, None)
    return HttpResponseRedirect(reverse('shop:login'))


class MemberCenterView(generic.TemplateView, BasicUserView):
    """个人中心视图"""

    template_name = 'shop/center/member_center/member_info.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(request=self.request, kwargs=kwargs)


def center_enter_view(request):
    """用户中心统一入口视图"""

    user = get_current_user(request)
    # 用户未登录时重定向到登录页面
    center_url = reverse('shop:login')

    # 判断用户类型并跳转到合适的用户中心
    if user is not None:
        if user.type_id == 1:
            center_url = reverse('shop:member_center')
        if user.type_id == 2:
            center_url = reverse('shop:member_center')
        if user.type_id == 3:
            center_url = reverse('shop:member_center')

    return HttpResponseRedirect(center_url)
