from django.test import TestCase

from .models import User, Goods


class GoodsModelTest(TestCase):

    def createGoodsTest(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        self.assertIn(u, User.objects.all())

        g = Goods.objects.create(goods_name='pc', seller=u, price=5999.99)
        self.assertIn(g, Goods.objects.all())
