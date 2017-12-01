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
