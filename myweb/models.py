# -*- coding: utf-8 -*
from django.db import models


class Users(models.Model):
    username = models.CharField(max_length=32)
    name = models.CharField(max_length=16)
    password = models.CharField(max_length=32)
    sex = models.IntegerField(default=1)
    address = models.CharField(max_length=255)
    code = models.CharField(max_length=6)
    phone = models.CharField(max_length=16)
    email = models.CharField(max_length=50)
    state = models.IntegerField(default=1)
    addtime = models.IntegerField()

    class Meta:
        db_table = "myweb_users"  


class Types(models.Model):
    name = models.CharField(max_length=32)
    pid = models.IntegerField(default=0)
    path = models.CharField(max_length=255)

    class Meta:
        db_table = "myweb_type"


class Goods(models.Model):
    typeid = models.IntegerField()
    goods = models.CharField(max_length=32)
    company = models.CharField(max_length=50)
    descr = models.TextField()
    price = models.FloatField()
    picname = models.CharField(max_length=255)
    state = models.IntegerField(default=1)
    store = models.IntegerField(default=0)
    num = models.IntegerField(default=0)
    clicknum = models.IntegerField(default=0)
    addtime = models.IntegerField()

    class Meta:
        db_table = "myweb_goods"

    def toDicts(self):
        return {'id': self.id, 'goods': self.goods, 'picname': self.picname, 'price': self.price, 'num': self.num, 'descr': self.descr}


class Cart(models.Model):
    uid = models.IntegerField()
    phone = models.CharField(max_length=16)
    addtime = models.IntegerField()
    price = models.IntegerField()
    number = models.IntegerField()
    total = models.FloatField()


class Store(models.Model):
    uid = models.IntegerField()
    good_id = models.IntegerField()
    addtime = models.IntegerField()
    price = models.IntegerField()
    number = models.IntegerField()

# 发货清单
class Dispatch(models.Model):
    uid = models.IntegerField()
    good_id = models.IntegerField()
    store_id = models.IntegerField()
    linkman = models.CharField(max_length=32)
    phone = models.CharField(max_length=16)
    address = models.CharField(max_length=255)
    code = models.CharField(max_length=6)
    addtime = models.IntegerField()
    number = models.IntegerField()
    status = models.IntegerField(default=0)


class Orders(models.Model):
    uid = models.IntegerField()
    goods = models.CharField(max_length=255)
    linkman = models.CharField(max_length=32)
    address = models.CharField(max_length=255)
    code = models.CharField(max_length=6)
    phone = models.CharField(max_length=16)
    addtime = models.IntegerField()
    total = models.FloatField()
    status = models.IntegerField(default=0)


class Detail(models.Model):
    orderid = models.IntegerField()
    goodsid = models.IntegerField()
    name = models.CharField(max_length=32)
    price = models.FloatField()
    num = models.IntegerField()
    class Meta:
        db_table = "detail" 


class Carousel(models.Model):
    typeid = models.IntegerField()
    goods = models.CharField(max_length=32)
    company = models.CharField(max_length=50)
    descr = models.TextField()
    price = models.FloatField()
    picname = models.CharField(max_length=255)
    state = models.IntegerField(default=1)
    store = models.IntegerField(default=0)
    num = models.IntegerField(default=0)
    clicknum = models.IntegerField(default=0)
    addtime = models.IntegerField()

    def __unicode__(self):
        return str(self.pk)