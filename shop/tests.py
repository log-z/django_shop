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
        self.assertContains(response, g.image.url)
        self.assertNotContains(response, 'default_goods_image.png')
        self.assertNotContains(response, g.description)

    def test_goods_search(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g1 = Goods.objects.create(goods_name='联想ThinkPad X390', seller=u, price=5999.99)
        g2 = Goods.objects.create(goods_name='2019新品天王表', seller=u, price=5999.99)
        g3 = Goods.objects.create(goods_name='2019版五年高考三年模拟', seller=u, price=5999.99)

        # 查找到单个结果
        response1 = self.client.get('/shop/', data={'g': 'think'})
        self.assertContains(response1, g1.goods_name)
        self.assertNotContains(response1, g2.goods_name)
        self.assertNotContains(response1, g3.goods_name)
        self.assertNotContains(response1, 'sorry，未搜索到合适的内容。')
        self.assertContains(response1, 'value="think"')

        # 查找到多个结果
        response2 = self.client.get('/shop/', data={'g': '2019'})
        self.assertNotContains(response2, g1.goods_name)
        self.assertContains(response2, g2.goods_name)
        self.assertContains(response2, g3.goods_name)

        # 查找不到任何结果
        response3 = self.client.get('/shop/', data={'g': '什么什么'})
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

        response1 = self.client.get('/shop/', data={'s': u1.id})
        self.assertContains(response1, g1.goods_name)
        self.assertContains(response1, g2.goods_name)
        self.assertNotContains(response1, g3.goods_name)
        self.assertNotContains(response1, 'sorry，未搜索到合适的内容。')

        response2 = self.client.get('/shop/', data={'s': u2.id})
        self.assertNotContains(response2, g1.goods_name)
        self.assertNotContains(response2, g2.goods_name)
        self.assertContains(response2, g3.goods_name)

        # 商家不存在
        response3 = self.client.get('/shop/', data={'s': 999999})
        self.assertEquals(response3.status_code, 404)

    def test_goods_search_and_seller_filter(self):
        u1 = User.objects.create(username='abc', password='123', email='a@qq.com')
        g1 = Goods.objects.create(goods_name='联想ThinkPad X390', seller=u1, price=5999.99)
        g2 = Goods.objects.create(goods_name='2019新品天王表', seller=u1, price=5999.99)

        u2 = User.objects.create(username='def', password='456', email='b@qq.com')
        g3 = Goods.objects.create(goods_name='2019版五年高考三年模拟', seller=u2, price=5999.99)

        # 商品搜索和商家过滤均命中
        response1 = self.client.get('/shop/', data={
            'g': '2019',
            's': u1.id,
        })
        self.assertNotContains(response1, g1.goods_name)
        self.assertContains(response1, g2.goods_name)
        self.assertNotContains(response1, g3.goods_name)

        # 商品搜索不命中，商家过滤命中
        response2 = self.client.get('/shop/', data={
            'g': '什么什么',
            's': u1.id,
        })
        self.assertContains(response2, 'sorry，未搜索到合适的内容。')

        # 商品搜索命中，商家过滤不命中
        response3 = self.client.get('/shop/', data={
            'g': '2019',
            's': 99999,
        })
        self.assertEquals(response3.status_code, 404)

        # 商品搜索和商家过滤均不命中
        response4 = self.client.get('/shop/', data={
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
        response1 = self.client.get('/shop/goods/{}'.format(g.id))
        self.assertContains(response1, g.seller.username)
        self.assertContains(response1, g.goods_name)
        self.assertContains(response1, g.price)
        self.assertContains(response1, 'default_goods_image.png')

        # 无效商品ID
        response2 = self.client.get('/shop/goods/99999')
        self.assertEquals(response2.status_code, 404)

    def test_full_object_show(self):
        u = User.objects.create(username='abc', password='123', email='a@qq.com')
        g = Goods.objects.create(goods_name='pc', seller=u, price=9.9, image='image.png', description='一些奇奇怪怪的描述')

        response1 = self.client.get('/shop/goods/{}'.format(g.id))
        self.assertContains(response1, g.image.url)
        self.assertContains(response1, g.description)
