from django.db import models

from .apps import ShopConfig

import uuid


# 媒体文件路径
MEDIA_DIR = '{}/'.format(ShopConfig.name)
# 图片媒体文件路径
IMAGE_DIR = '{}image/'.format(MEDIA_DIR)


def goods_image_custom_path(_, filename):
    """生成商品图片路径"""

    ext = filename.split('.')[-1]
    filename = '{}goods/{}.{}'.format(IMAGE_DIR, uuid.uuid4().hex, ext)
    return filename


class User(models.Model):
    """用户模型"""

    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=320)

    def __str__(self):
        return self.username


class Goods(models.Model):
    """商品模型"""

    goods_name = models.CharField(max_length=40)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to=goods_image_custom_path)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.goods_name
