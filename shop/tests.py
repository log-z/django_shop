from django.test import TestCase

from .models import User, Goods


class UserModelTest(TestCase):
    """用户模型测试"""

    def createUserTest(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        self.assertIn(u, User.objects.all())


class GoodsModelTest(TestCase):
    """商品模型测试"""

    def createGoodsTest(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=5999.99)
        self.assertIn(g, Goods.objects.all())
