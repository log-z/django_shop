from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .apps import ShopConfig

import uuid
import bcrypt


# 媒体文件路径
MEDIA_DIR = '{}/'.format(ShopConfig.name)
# 图片媒体文件路径
IMAGE_DIR = '{}image/'.format(MEDIA_DIR)


def goods_image_custom_path(_, filename):
    """生成商品图片路径"""

    ext = filename.split('.')[-1]
    filename = '{}goods/{}.{}'.format(IMAGE_DIR, uuid.uuid4().hex, ext)
    return filename


class UserType(models.Model):
    """用户类型模型"""

    typename = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.typename


class User(models.Model):
    """用户模型"""

    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=60)
    email = models.CharField(max_length=320)
    type = models.ForeignKey(UserType, on_delete=models.PROTECT, default=UserType.objects.get(typename='normal').pk)

    SALT_ROUNDS = 12
    SALT_PREFIX = b'2b'

    def __str__(self):
        return self.username

    def check_password(self, pw):
        """验证密码是否正确"""

        try:
            checked = bcrypt.checkpw(password=pw.encode('utf-8'), hashed_password=self.password.encode('utf-8'))
        except ValueError:
            checked = False
        return checked


class Goods(models.Model):
    """商品模型"""

    goods_name = models.CharField(max_length=40)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to=goods_image_custom_path)
    description = models.TextField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.goods_name


@receiver(pre_save, sender=User)
def before_user_save(_, instance, **__):
    """保存用户的修改之前将调用此函数"""

    old_object = User.objects.get(id=instance.id)
    if not old_object.check_password(instance.password):
        salt = bcrypt.gensalt(rounds=User.SALT_ROUNDS, prefix=User.SALT_PREFIX)
        instance.password = bcrypt.hashpw(password=instance.password.encode('utf-8'), salt=salt).decode('utf-8')
