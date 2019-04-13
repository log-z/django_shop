from django.test import TestCase

from .models import User, Goods


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

    def test_base_object_show(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=5999.99)

        response = self.client.get('/shop/')
        self.assertContains(response, g.goods_name)
        self.assertContains(response, g.seller)
        self.assertContains(response, g.price)
        self.assertContains(response, 'default_goods_image.png')

    def test_full_object_show(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=9.9, image='image.png', description='一些奇奇怪怪的描述')

        response = self.client.get('/shop/')
        self.assertNotContains(response, g.description)
        self.assertNotContains(response, 'default_goods_image.png')
        self.assertContains(response, 'image.png')


# TODO: 未完成商品检索测试
