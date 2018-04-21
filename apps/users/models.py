from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
from tinymce.models import HTMLField
from utils.models import BaseModel

class  User(BaseModel,AbstractUser):
    """模型管理类"""
    class Meta(object):
        # 指定表名
        db_table = 'df_user'

class Address(BaseModel):
    """地址"""
    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"

class TestModel(BaseModel):
    """测试用"""
    name = models.CharField(max_length=20)
    # 使用第三方的：HTMLField
    goods_detail=HTMLField(default='',verbose_name='商品详情')
    # 定义元组
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )
    status =models.SmallIntegerField(default=1,
                                     verbose_name='订单状态',
                                     choices=ORDER_STATUS_CHOICES)  # choices=元组
    class Meta(object):
        db_table='df_test'
        # 指定模型在后台显示的内容
        verbose_name='测试模型'
        # 去除后台显示的名称默认添加的's'
        verbose_name_plural = verbose_name

