import hashlib

from django.test import TestCase, Client
from django.shortcuts import reverse

from .models import User, Goods
from .forms import RegisterBEForm, RegisterFEForm, LoginBEForm, LoginFEForm


class UserModelTest(TestCase):
    """用户模型测试"""

    def test_create_user(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        self.assertIn(u, User.objects.all())


class GoodsModelTest(TestCase):
    """商品模型测试"""

    def test_create_goods(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=5999.99)
        self.assertIn(g, Goods.objects.all())


class GoodsListViewTest(TestCase):
    """商品列表视图测试"""

    url = reverse('shop:goods_list')

    def test_base_object_show(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=5999.99)

        response = self.client.get(self.url)
        self.assertContains(response, g.goods_name)
        self.assertContains(response, g.seller)
        self.assertContains(response, g.price)
        self.assertContains(response, 'default_goods_image.png')

    def test_full_object_show(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=9.9, image='image.png', description='一些奇奇怪怪的描述')

        response = self.client.get(self.url)
        self.assertContains(response, g.image.url)
        self.assertNotContains(response, 'default_goods_image.png')
        self.assertNotContains(response, g.description)

    def test_goods_search(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g1 = Goods.objects.create(goods_name='联想ThinkPad X390', seller=u, price=5999.99)
        g2 = Goods.objects.create(goods_name='2019新品天王表', seller=u, price=5999.99)
        g3 = Goods.objects.create(goods_name='2019版五年高考三年模拟', seller=u, price=5999.99)

        # 查找到单个结果
        response1 = self.client.get(self.url, data={'g': 'think'})
        self.assertContains(response1, g1.goods_name)
        self.assertNotContains(response1, g2.goods_name)
        self.assertNotContains(response1, g3.goods_name)
        self.assertNotContains(response1, 'sorry，未搜索到合适的内容。')
        self.assertContains(response1, 'value="think"')

        # 查找到多个结果
        response2 = self.client.get(self.url, data={'g': '2019'})
        self.assertNotContains(response2, g1.goods_name)
        self.assertContains(response2, g2.goods_name)
        self.assertContains(response2, g3.goods_name)

        # 查找不到任何结果
        response3 = self.client.get(self.url, data={'g': '什么什么'})
        self.assertNotContains(response3, g1.goods_name)
        self.assertNotContains(response3, g2.goods_name)
        self.assertNotContains(response3, g3.goods_name)
        self.assertContains(response3, 'sorry，未搜索到合适的内容。')

    def test_seller_filter(self):
        u1 = User.objects.create(username='abc', password='123', email='a@qq.com')
        g1 = Goods.objects.create(goods_name='联想ThinkPad X390', seller=u1, price=5999.99)
        g2 = Goods.objects.create(goods_name='2019新品天王表', seller=u1, price=5999.99)

        u2 = User.objects.create(username='def', password='456', email='b@qq.com')
        g3 = Goods.objects.create(goods_name='2019版五年高考三年模拟', seller=u2, price=5999.99)

        response1 = self.client.get(self.url, data={'s': u1.id})
        self.assertContains(response1, g1.goods_name)
        self.assertContains(response1, g2.goods_name)
        self.assertNotContains(response1, g3.goods_name)
        self.assertNotContains(response1, 'sorry，未搜索到合适的内容。')

        response2 = self.client.get(self.url, data={'s': u2.id})
        self.assertNotContains(response2, g1.goods_name)
        self.assertNotContains(response2, g2.goods_name)
        self.assertContains(response2, g3.goods_name)

        # 商家不存在
        response3 = self.client.get(self.url, data={'s': 999999})
        self.assertEquals(response3.status_code, 404)

    def test_goods_search_and_seller_filter(self):
        u1 = User.objects.create(username='abc', password='123', email='a@qq.com')
        g1 = Goods.objects.create(goods_name='联想ThinkPad X390', seller=u1, price=5999.99)
        g2 = Goods.objects.create(goods_name='2019新品天王表', seller=u1, price=5999.99)

        u2 = User.objects.create(username='def', password='456', email='b@qq.com')
        g3 = Goods.objects.create(goods_name='2019版五年高考三年模拟', seller=u2, price=5999.99)

        # 商品搜索和商家过滤均命中
        response1 = self.client.get(self.url, data={
            'g': '2019',
            's': u1.id,
        })
        self.assertNotContains(response1, g1.goods_name)
        self.assertContains(response1, g2.goods_name)
        self.assertNotContains(response1, g3.goods_name)

        # 商品搜索不命中，商家过滤命中
        response2 = self.client.get(self.url, data={
            'g': '什么什么',
            's': u1.id,
        })
        self.assertContains(response2, 'sorry，未搜索到合适的内容。')

        # 商品搜索命中，商家过滤不命中
        response3 = self.client.get(self.url, data={
            'g': '2019',
            's': 99999,
        })
        self.assertEquals(response3.status_code, 404)

        # 商品搜索和商家过滤均不命中
        response4 = self.client.get(self.url, data={
            'g': '什么什么',
            's': 99999,
        })
        self.assertEquals(response4.status_code, 404)


class GoodsDetailViewTest(TestCase):
    """商品详情视图测试"""

    def test_base_object_show(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=5999.99)

        # 有效商品ID
        url1 = reverse('shop:goods_detail', kwargs={'pk': g.id})
        response1 = self.client.get(url1)
        self.assertContains(response1, g.seller.username)
        self.assertContains(response1, g.goods_name)
        self.assertContains(response1, g.price)
        self.assertContains(response1, 'default_goods_image.png')

        # 无效商品ID
        url2 = reverse('shop:goods_detail', kwargs={'pk': 99999})
        response2 = self.client.get(url2)
        self.assertEquals(response2.status_code, 404)

    def test_full_object_show(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=9.9, image='image.png', description='一些奇奇怪怪的描述')

        url1 = reverse('shop:goods_detail', kwargs={'pk': g.id})
        response1 = self.client.get(url1)
        self.assertContains(response1, g.image.url)
        self.assertContains(response1, g.description)


class RegisterFEFormTest(TestCase):
    """前端注册表单测试"""

    def test_valid_form(self):
        # 最小长度的前端有效注册信息
        form1 = RegisterFEForm({
            'username': '123',
            'email': 'a@b.com',
            'password': '12345678',
            'password_again': '12345678',
        })
        self.assertTrue(form1.is_valid())

        # 最大长度的前端有效注册信息
        form2 = RegisterFEForm({
            'username': '12345678901234567890',
            'email': 'aaaaaaaaaaaaaa@bbbbbbbbbbbbbb.commmmmmmmmmmmmm',
            'password': '12345678901234567890',
            'password_again': '12345678901234567890',
        })
        self.assertTrue(form2.is_valid())

    def test_blank_form(self):
        form = RegisterFEForm()
        self.assertFalse(form.is_valid())

    def test_invalid_username(self):
        data = {
            'email': 'a@b.com',
            'password': '12345678',
            'password_again': '12345678',
        }

        # 不指定用户名
        form1 = RegisterFEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的用户名
        data['username'] = '12'
        form2 = RegisterFEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的用户名
        data['username'] = '12345678901234567890a'
        form3 = RegisterFEForm(data)
        self.assertFalse(form3.is_valid())

    def test_invalid_email(self):
        data = {
            'username': '123',
            'password': '12345678',
            'password_again': '12345678',
        }

        # 不指定Email
        form1 = RegisterFEForm(data)
        self.assertFalse(form1.is_valid())

        # 不带“@”的Email
        data['email'] = 'ab.com'
        form2 = RegisterFEForm(data)
        self.assertFalse(form2.is_valid())

        # 不带域名的Email
        data['email'] = 'a@b'
        form3 = RegisterFEForm(data)
        self.assertFalse(form3.is_valid())

    def test_invalid_password(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password_again': '12345678',
        }

        # 不指定密码
        form1 = RegisterFEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的密码
        data['password'] = '1234567'
        form2 = RegisterFEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的密码
        data['password'] = '12345678901234567890a'
        form3 = RegisterFEForm(data)
        self.assertFalse(form3.is_valid())

    def test_invalid_password_again(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': '12345678',
        }

        # 不指定重输的密码
        form1 = RegisterFEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的重输的密码
        data['password_again'] = '1234567'
        form2 = RegisterFEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的重输的密码
        data['password_again'] = '12345678901234567890a'
        form3 = RegisterFEForm(data)
        self.assertFalse(form3.is_valid())


class RegisterBEFormTest(TestCase):
    """后端注册表单测试"""

    def test_valid_form(self):
        # 最小长度的后端有效注册信息
        form1 = RegisterBEForm({
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        })
        self.assertTrue(form1.is_valid())

        # 最大长度的后端有效注册信息
        form2 = RegisterBEForm({
            'username': '12345678901234567890',
            'email': 'aaaaaaaaaaaaaa@bbbbbbbbbbbbbb.commmmmmmmmmmmmm',
            'password': hashlib.sha256(b'12345678901234567890').hexdigest(),
        })
        self.assertTrue(form2.is_valid())

    def test_blank_form(self):
        form = RegisterBEForm()
        self.assertFalse(form.is_valid())

    def test_invalid_username(self):
        data = {
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }

        # 不指定用户名
        form1 = RegisterBEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的用户名
        data['username'] = '12'
        form2 = RegisterBEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的用户名
        data['username'] = '12345678901234567890a'
        form3 = RegisterBEForm(data)
        self.assertFalse(form3.is_valid())

    def test_invalid_email(self):
        data = {
            'username': '123',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }

        # 不指定Email
        form1 = RegisterBEForm(data)
        self.assertFalse(form1.is_valid())

        # 不带“@”的Email
        data['email'] = 'ab.com'
        form2 = RegisterBEForm(data)
        self.assertFalse(form2.is_valid())

        # 不带域名的Email
        data['email'] = 'a@b'
        form3 = RegisterBEForm(data)
        self.assertFalse(form3.is_valid())

    def test_invalid_password(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
        }

        # 不指定密码
        form1 = RegisterBEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的密码
        data['password'] = hashlib.sha256(b'1').hexdigest()[:-1]
        form2 = RegisterBEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的密码
        data['password'] = hashlib.sha256(b'12345678').hexdigest() + 'a'
        form3 = RegisterBEForm(data)
        self.assertFalse(form3.is_valid())


class LoginFEFormTest(TestCase):
    """前端登陆表单测试"""

    def test_valid_form(self):
        # 最小长度的前端有效登陆信息
        form1 = LoginFEForm({
            'username': '123',
            'password': '12345678',
        })
        self.assertTrue(form1.is_valid())

        # 最大长度的前端有效登陆信息
        form2 = LoginFEForm({
            'username': '12345678901234567890',
            'password': '12345678901234567890',
        })
        self.assertTrue(form2.is_valid())

    def test_blank_form(self):
        form = LoginFEForm()
        self.assertFalse(form.is_valid())

    def test_invalid_username(self):
        data = {
            'password': '12345678',
        }

        # 不指定用户名
        form1 = LoginFEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的用户名
        data['username'] = '12'
        form2 = LoginFEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的用户名
        data['username'] = '12345678901234567890a'
        form3 = LoginFEForm(data)
        self.assertFalse(form3.is_valid())

    def test_invalid_password(self):
        data = {
            'username': '123',
        }

        # 不指定密码
        form1 = LoginFEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的密码
        data['password'] = '1234567'
        form2 = LoginFEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的密码
        data['password'] = '12345678901234567890a'
        form3 = LoginFEForm(data)
        self.assertFalse(form3.is_valid())


class LoginBEFormTest(TestCase):
    """后端登陆表单测试"""

    def test_valid_form(self):
        # 最小长度的后端有效登陆信息
        form1 = LoginBEForm({
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        })
        self.assertTrue(form1.is_valid())

        # 最大长度的后端有效登陆信息
        form2 = LoginBEForm({
            'username': '12345678901234567890',
            'email': 'aaaaaaaaaaaaaa@bbbbbbbbbbbbbb.commmmmmmmmmmmmm',
            'password': hashlib.sha256(b'12345678901234567890').hexdigest(),
        })
        self.assertTrue(form2.is_valid())

    def test_blank_form(self):
        form = LoginBEForm()
        self.assertFalse(form.is_valid())

    def test_invalid_username(self):
        data = {
            'email': 'a@b.com',
            'password': '12345678',
        }

        # 不指定用户名
        form1 = LoginBEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的用户名
        data['username'] = '12'
        form2 = LoginBEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的用户名
        data['username'] = '12345678901234567890a'
        form3 = LoginBEForm(data)
        self.assertFalse(form3.is_valid())

    def test_invalid_password(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
        }

        # 不指定密码
        form1 = LoginBEForm(data)
        self.assertFalse(form1.is_valid())

        # 长度过短的密码
        data['password'] = hashlib.sha256(b'1').hexdigest()[:-1]
        form2 = LoginBEForm(data)
        self.assertFalse(form2.is_valid())

        # 超出长度的密码
        data['password'] = hashlib.sha256(b'12345678').hexdigest() + 'a'
        form3 = LoginBEForm(data)
        self.assertFalse(form3.is_valid())


class RegisterViewTest(TestCase):
    """注册视图测试"""

    url = reverse('shop:register')
    register_view_identity = '已有账号，我要登陆'

    def test_not_logged(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.register_view_identity)
        self.assertNotContains(response, reverse('shop:logout'))

    def test_csrf(self):
        # 测试CSRF是否可用
        response1 = self.client.get(self.url)
        self.assertContains(response1, 'csrfmiddlewaretoken')

        # 测试无CSRFToken的空提交
        client = Client(enforce_csrf_checks=True)
        response2 = client.post(self.url)
        self.assertEqual(response2.status_code, 403)

        # 测试带CSRFToken的空提交
        response3 = self.client.post(self.url)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.register_view_identity)
        self.assertFalse(User.objects.all().exists())

    def test_valid_submit(self):
        # 最小长度的后端有效注册信息
        data1 = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
            'password_again': hashlib.sha256(b'12345678').hexdigest(),
        }
        response1 = self.client.post(self.url, data=data1)
        self.assertEqual(response1.status_code, 302)
        self.assertTrue(User.objects.filter(email=data1['email']).exists())
        self.client.cookies.clear()
        User.objects.all().delete()

        # 最大长度的后端有效注册信息
        data2 = {
            'username': '12345678901234567890',
            'email': 'aaaaaaaaaaaaaa@bbbbbbbbbbbbbb.com',
            'password': hashlib.sha256(b'12345678901234567890').hexdigest(),
            'password_again': hashlib.sha256(b'12345678901234567890').hexdigest(),
        }
        response2 = self.client.post(self.url, data=data2)
        self.assertEqual(response2.status_code, 302)
        self.assertTrue(User.objects.filter(email=data2['email']).exists())
        self.client.cookies.clear()
        User.objects.all().delete()

    def test_invalid_username(self):
        data = {
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
            'password_again': hashlib.sha256(b'12345678').hexdigest(),
        }

        # 不指定用户名
        response1 = self.client.post(self.url, data=data)
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

        # 长度过短的用户名
        data['username'] = '12'
        response2 = self.client.post(self.url, data=data)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

        # 超出长度的用户名
        data['username'] = '12345678901234567890a'
        response3 = self.client.post(self.url, data=data)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

    def test_invalid_email(self):
        data = {
            'username': '123',
            'password': hashlib.sha256(b'12345678').hexdigest(),
            'password_again': hashlib.sha256(b'12345678').hexdigest(),
        }

        # 不指定Email
        response1 = self.client.post(self.url, data=data)
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, self.register_view_identity)
        self.assertFalse(User.objects.all().exists())

        # 不带“@”的Email
        data['email'] = 'ab.com'
        response2 = self.client.post(self.url, data=data)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

        # 不带域名的Email
        data['email'] = 'a@b'
        response3 = self.client.post(self.url, data=data)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

    def test_invalid_password(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
        }

        # 不指定密码
        response1 = self.client.post(self.url, data=data)
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

        # 长度过短的密码
        data['password'] = hashlib.sha256(b'1').hexdigest()[:-1]
        data['password_again'] = hashlib.sha256(b'1').hexdigest()[:-1]
        response2 = self.client.post(self.url, data=data)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

        # 超出长度的密码
        data['password'] = hashlib.sha256(b'12345678').hexdigest() + 'a'
        data['password_again'] = hashlib.sha256(b'12345678').hexdigest() + 'a'
        response3 = self.client.post(self.url, data=data)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

        # 两次输入的密码不一致
        data['password'] = hashlib.sha256(b'12345678').hexdigest()
        data['password_again'] = hashlib.sha256(b'87654321').hexdigest()
        response3 = self.client.post(self.url, data=data)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.register_view_identity)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

    def test_is_logged(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }
        User.objects.create(**data)

        # 登陆
        response1 = self.client.post(reverse('shop:login'), data=data)
        self.assertEqual(response1.status_code, 302)

        # 登陆
        response2 = self.client.post(self.url, data=data)
        self.assertEqual(response2.status_code, 302)

        # 登陆
        response3 = self.client.get(self.url, data=data)
        self.assertEqual(response3.status_code, 302)


class LoginViewTest(TestCase):
    """登陆视图测试"""

    url = reverse('shop:login')
    login_view_identity = '还没账号，我要注册'

    def test_not_logged(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.login_view_identity)
        self.assertNotContains(response, reverse('shop:logout'))

    def test_csrf(self):
        # 测试CSRF是否可用
        response1 = self.client.get(self.url)
        self.assertContains(response1, 'csrfmiddlewaretoken')

        # 测试无CSRFToken的空提交
        client = Client(enforce_csrf_checks=True)
        response2 = client.post(self.url)
        self.assertEqual(response2.status_code, 403)

        # 测试带CSRFToken的空提交
        response3 = self.client.post(self.url)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.login_view_identity)
        self.assertNotContains(response3, reverse('shop:logout'))

    def test_valid_submit(self):
        # 最小长度的后端有效登陆信息
        data1 = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }
        User.objects.create(**data1)
        response1 = self.client.post(self.url, data=data1)
        self.assertEqual(response1.status_code, 302)
        self.client.cookies.clear()

        # 最大长度的后端有效登陆信息
        data2 = {
            'username': '12345678901234567890',
            'email': 'aaaaaaaaaaaaaa@bbbbbbbbbbbbbb.com',
            'password': hashlib.sha256(b'12345678901234567890').hexdigest(),
        }
        User.objects.create(**data2)
        response2 = self.client.post(self.url, data=data2)
        self.assertEqual(response2.status_code, 302)
        self.client.cookies.clear()

    def test_invalid_username(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }
        User.objects.create(**data)

        # 不指定用户名
        del data['username']
        response1 = self.client.post(self.url, data=data)
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, self.login_view_identity)
        self.assertNotContains(response1, reverse('shop:logout'))

        # 长度过短的用户名
        data['username'] = '12'
        response2 = self.client.post(self.url, data=data)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, self.login_view_identity)
        self.assertNotContains(response2, reverse('shop:logout'))

        # 超出长度的用户名
        data['username'] = '12345678901234567890a'
        response3 = self.client.post(self.url, data=data)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.login_view_identity)
        self.assertNotContains(response3, reverse('shop:logout'))

        # 错误的用户名
        data['username'] = '321'
        response4 = self.client.post(self.url, data=data)
        self.assertEqual(response4.status_code, 200)
        self.assertContains(response3, self.login_view_identity)
        self.assertNotContains(response3, reverse('shop:logout'))

    def test_invalid_password(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }
        User.objects.create(**data)

        # 不指定密码
        del data['password']
        response1 = self.client.post(self.url, data=data)
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, self.login_view_identity)
        self.assertNotContains(response1, reverse('shop:logout'))

        # 长度过短的密码
        data['password'] = hashlib.sha256(b'12345678').hexdigest()[:-1]
        response2 = self.client.post(self.url, data=data)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, self.login_view_identity)
        self.assertNotContains(response2, reverse('shop:logout'))

        # 超出长度的密码
        data['password'] = hashlib.sha256(b'12345678').hexdigest() + 'a'
        response3 = self.client.post(self.url, data=data)
        self.assertEqual(response3.status_code, 200)
        self.assertContains(response3, self.login_view_identity)
        self.assertNotContains(response3, reverse('shop:logout'))

        # 错误的密码
        data['password'] = hashlib.sha256(b'87654321').hexdigest()
        response4 = self.client.post(self.url, data=data)
        self.assertEqual(response4.status_code, 200)
        self.assertContains(response3, self.login_view_identity)
        self.assertNotContains(response3, reverse('shop:logout'))

    def test_is_logged(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }
        User.objects.create(**data)

        # 登陆
        response1 = self.client.post(self.url, data=data)
        self.assertEqual(response1.status_code, 302)

        # 登陆
        response2 = self.client.post(self.url, data=data)
        self.assertEqual(response2.status_code, 302)

        # 登陆
        response3 = self.client.get(self.url, data=data)
        self.assertEqual(response3.status_code, 302)


class LogoutViewTest(TestCase):
    """退出登陆视图测试"""

    def test_user_logout(self):
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }
        User.objects.create(**data)

        # 登陆
        response1 = self.client.post(reverse('shop:login'), data=data)
        self.assertEqual(response1.status_code, 302)
        # 退出
        response2 = self.client.get(reverse('shop:logout'))
        self.assertEqual(response2.status_code, 302)
        # 检查退出状态
        response3 = self.client.get(reverse('shop:goods_list'))
        self.assertNotContains(response3, reverse('shop:logout'))


class BaseViewTest(TestCase):
    """基本（通用）视图测试"""

    def test_user_center_enter(self):
        # 已登录状态
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }

        User.objects.create(**data)
        self.client.post(reverse('shop:login'), data=data)

        response2 = self.client.get(reverse('shop:goods_list'))
        self.assertContains(response2, reverse('shop:logout'))

    def test_logged_user_is_no_found(self):
        # 已登录状态，但用户被删除
        data = {
            'username': '123',
            'email': 'a@b.com',
            'password': hashlib.sha256(b'12345678').hexdigest(),
        }
        user = User.objects.create(**data)

        self.client.post(reverse('shop:login'), data=data)
        user.delete()

        response2 = self.client.get(reverse('shop:goods_list'))
        self.assertEqual(response2.status_code, 200)
        self.assertNotContains(response2, reverse('shop:logout'))
