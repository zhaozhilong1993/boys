# -*- coding: utf-8 -*
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from itertools import chain
import random
import hashlib
import io
import time
import json

from myweb.models import Types, Goods, Users, Orders, Detail, Carousel, Store, Dispatch


# 公共信息加载函数
def loadinfo():
    context={}
    context['type0list'] = Types.objects.filter(pid=0)
    return context


# 网站首页
def index(request):
    context = {}
    context['type0list'] = Types.objects.filter(pid=0)
    context['luntu_list'] = Carousel.objects.all().order_by('-pk')[:5]
    return render(request, "myweb/index.html", context)


# 商品列表页
def list(request):
    context = loadinfo()
    list = Goods.objects.filter()
    if request.GET.get('tid', '') != '':
        tid = str(request.GET.get('tid', ''))
        list = list.filter(typeid__in=Types.objects.only('id').filter(path__contains=','+tid+','))
    context['goodslist'] = list
    return render(request, "myweb/list.html", context)


# 商品详情页
def detail(request, gid):
    context = loadinfo()
    ob = Goods.objects.get(id=gid)
    ob.clicknum += 1
    ob.save()
    context['goods'] = ob
    return render(request, "myweb/detail.html", context)


#  注册页
def register(request):
    return render(request, "myweb/register.html")


# 注册操作
def registerzc(request):
    try:
        users = Users.objects.all()
        if users.filter(phone=request.POST['phone']):
            context = {'info': '手机号已存在！'}
        else:
            ob = Users()
            ob.username = request.POST['username']
            ob.name = request.POST['name']
            # 获取密码并md5
            import hashlib
            m = hashlib.md5()
            m.update(bytes(request.POST['password']))
            ob.password = m.hexdigest()
            ob.phone = request.POST['phone']
            ob.email = request.POST['email']
            ob.state = 1
            ob.addtime = time.time()
            ob.save()
            context = {'info': '添加成功！'}
    except:
        context = {'info': '添加失败！'}
    # return render(request, "myweb/info.html", context)
    return render(request, "myweb/login.html")

# 登陆页
def login(request):
    return render(request, "myweb/login.html")


# 登陆操作
def logindl(request):
    try:
        user = Users.objects.get(phone=request.POST['phone'])
        # 根据账号获取登陆着信息
        m = hashlib.md5()
        m.update(bytes(request.POST['password']))
        if user.password == m.hexdigest():
            # 若此处登陆成功，将 当前登陆信息放到session中，并跳转页面
            request.session['username'] = user.username
            request.session['uid'] = user.id
            request.session['user_address'] = user.address
            request.session['user_code'] = user.code
            request.session['user_phone'] = user.phone
            return redirect(reverse('index'))
        else:
            context = {'info': '登陆密码出错！'}
            return render(request, "myweb/login.html", context)

    except:
        context = {'info': '账号不存在！'}
        return render(request, "myweb/login.html", context)


# 退出页
def loginout(request):
    del request.session['username']
    del request.session['uid']
    del request.session['user_address']
    del request.session['user_phone']
    del request.session['user_code']
    return redirect(reverse('index'))


# 个人中心页
def member(request):
    user = Users.objects.get(id=request.session['uid'])
    message_list = {'message_list': user}
    return render(request, "myweb/member.html", message_list)


# 修改个人中心
def edit_member(request):
    user = Users.objects.get(id=request.session['uid'])
    message_list = {'message_list': user}
    return render(request, "myweb/edit_member.html", message_list)


# 修改个人信息
def edit_memberxg(request):
    try:
        ob = Users.objects.get(id=request.session['uid'])
        ob.name = request.POST['name']
        ob.sex = request.POST['sex']
        ob.address = request.POST['address']
        ob.code = request.POST['code']
        ob.phone = request.POST['phone']
        ob.email = request.POST['email']
        ob.save()
    except:
        context = {'info': '修改失败！'}
        return render(request, "myweb/info.html", context)
    return redirect(reverse('member'))


# 购物车
def cart(request):
    context = loadinfo()
    try:
        request.session['shoplist']
        return render(request, "myweb/cart.html", context)
    except:
        return redirect(reverse('index'))


# 清空购物车
def cartclear(request):
    context = loadinfo()
    request.session['shoplist'] = {}
    return redirect(reverse('cart'))


# 购物车内删除商品
def cartdel(request, sid):
    shoplist = request.session['shoplist']
    del shoplist[sid]
    request.session['shoplist'] = shoplist
    return redirect(reverse('cart'))


# 添加商品到购物车
def cartadd(request, sid):
    # 获取要放入购物车中的商品信息
    goods = Goods.objects.get(id=sid)
    shop = goods.toDicts()
    shop['shop_num'] = int(request.POST['shop_num'])  # 添加购买数量
    # 从session获取购物车信息
    if 'shoplist' in request.session:
        shoplist = request.session['shoplist']

    else:
        shoplist = {}

    # 判断此商品是否在购物车中
    if sid in shoplist:
        # 商品数量加一
        shoplist[sid]['shop_num'] += shop['shop_num']
    else:
        # 新商品添加
        shoplist[sid] = shop

    # 将购物车信息放回session
    # shoplist[1234567890] = request.session['uid']
    request.session['shoplist'] = shoplist
    print(shoplist)
    return redirect(reverse('cart'))


# 购物车商品加减
def cartchange(request):
    context = loadinfo()
    shoplist = request.session['shoplist']
    # 获取信息
    shopid = request.GET['sid']
    num = int(request.GET['num'])
    if num < 1:
        num = 1
    shoplist[shopid]['shop_num'] = num  # 更改商品数量
    request.session['shoplist'] = shoplist
    return render(request, 'myweb/cart.html', context)


# =========订单处理============
# 订单表单页
def orderform(request):
    # 获取要结账的商品id
    ids = request.GET['gids']
    if ids == '':
        return HttpResponse('请选择要结账的商品')
    gids = ids.split(',')
    # 获取购物车中的商品信息
    shoplist = request.session['shoplist']
    # 封装要结账的商品信息，以及累加总金额
    orderlist = {}
    total = 0
    for sid in gids:
        orderlist[sid] = shoplist[sid]
        total += shoplist[sid]['price']*shoplist[sid]['shop_num']
    request.session['orderlist'] = orderlist
    request.session['total'] = total
    return render(request, 'myweb/orderform.html')


# 订单确认页
def orderqr(request):
    request.session['order_username'] = request.POST['name']
    request.session['user_phone'] = request.POST['phone']
    return render(request, 'myweb/order_confirm.html')


# 将订单信息存入订单表和订单详情表
def orderxd(request):
    ord = Orders()
    ord.uid = request.session['uid']
    ord.linkman = request.session['order_username']
    ord.address = request.session['user_address']
    ord.code = request.session['user_code']
    ord.phone = request.session['user_phone']
    # 记录购买的商品情况
    ord.goods = json.dumps(request.session['orderlist'])

    # 支付完成后
    ord.status = 2

    ord.addtime = time.time()
    ord.total = request.session['total']
    ord.save()

    # 添加库存 - 新增
    goods_list = json.loads(ord.goods)
    for good_id,good_info in goods_list.items():
        store_room = Store()
        store_room.uid = ord.uid
        store_room.good_id = good_id
        store_room.price = good_info['price']
        store_room.number = good_info['shop_num']
        store_room.addtime = time.time()
        store_room.save()

    # 获取订单详情
    orderlist = request.session['orderlist']
    shoplist = request.session['shoplist']
    for shop in orderlist.values():
        del shoplist[str(shop['id'])]
        det = Detail()
        det.orderid = ord.id
        det.goodsid = shop['id']
        det.name = shop['goods']
        det.price = shop['price']
        det.num = shop['shop_num']
        det.save()

    # 在购物车中删除以购买的商品
    del request.session['orderlist']
    del request.session['total']
    request.session['shoplist'] = shoplist

    return redirect(reverse('myorder'))


# 我的订单页
def myorder(request):
    # if Orders.objects.filter(uid=request.session['uid']):
    #     context = {}
    #     context['ord_list'] = Orders.objects.all()
    #     return render(request, 'myweb/order.html', context)
    # else:
    #     return render(request, 'myweb/member.html')

    context = loadinfo()
    # 从session中获取登陆者的id号,并且从订单表orders中获取当前用户的所用订单
    orders = Orders.objects.filter(uid=request.session['uid'])
    dlist = []
    # 遍历当前用户的所有订单属性,并获得对应的订单详情信息
    for order in orders:
        dlist = Detail.objects.filter(orderid=order.id)
        order.detail_list = dlist
        # 图片信息
        for detail in dlist:
            goods = Goods.objects.get(id=detail.goodsid)
            detail.picname = goods.picname
    context['orders'] = orders
    context['dlist'] = dlist
    return render(request, "myweb/order_n.html", context)


# 订单详情
def orderxq(request):
    det = Detail.objects.filter(orderid=request.GET['oid'])
    for de in det:
        dt = Goods.objects.get(id=de.goodsid)
        de.picname = dt.picname
    context = {'detail_list': det}
    return render(request, 'myweb/orderxq.html', context)


# 状态修改
def orderztxg(request, gid):
    ob = Orders.objects.get(id=gid)
    ob.status = request.POST['status']
    ob.save()
    return redirect(reverse('myorder'))



# 订单信息显示页面
# def orderxs(request):
#     context = loadinfo()
#     # 从session中获取登陆者的id号,并且从订单表orders中获取当前用户的所用订单
#     orders = Orders.objects.filter(uid=request.session['user']['id'])
#     # 遍历当前用户的所有订单属性,并获得对应的订单详情信息
#     for order in orders:
#         dlist = Detail.objects.filter(orderid=order.id)
#         order.detail_list = dlist
#         # 图片信息
#         for detail in dlist:
#             goods = Goods.objects.get(id=detail.goodsid)
#             detail.picname = goods.picname
#     context['orders'] = orders
#     context['dlist'] = dlist
#     return render(request, "myweb/order_n.html", context)

# =========库存处理============
# 库存页
def store(request):
    context = loadinfo()
    # 从session中获取登陆者的id号,并且从库存表store中获取当前用户的信息
    store_room = Store.objects.filter(uid=request.session['uid'])
    dlist = []
    for i in store_room:
        good = Goods.objects.get(id=i.good_id)
        dlist.append(
            {
                'price': i.price,
                'number': i.number,
                'name': good.goods,
                'picname': good.picname,
                'addtime': i.addtime,
                'id': i.id
            }
        )
    context['store_room'] = dlist
    return render(request, "myweb/store.html", context)

# 库存-发货信息
def store_order(request):
    context = loadinfo()
    dispatch = Dispatch.objects.filter(uid=request.session['uid'])
    dlist = []
    for i in dispatch:
        good = Goods.objects.get(id=i.good_id)
        store_good = Store.objects.get(id=i.store_id)
        dlist.append(
            {
                'price': store_good.price, # 入库价
                'number': i.number, # 发货数量
                'remain': store_good.number, # 剩余库存
                'name': good.goods, # 商品名
                'picname': good.picname, # 商品图片
                'addtime': i.addtime, # 添加时间
                'status': i.status, # 发货状态
                'linkman': i.linkman, # 收货人
                'total': i.number * store_good.price,
                'id': i.id # 发货编号
            }
        )
    context['dispatch_order'] = dlist
    return render(request, 'myweb/store_order.html', context)

# 库存-发货页
def store_send(request):
    request.session['send_store_good_id'] = request.POST['send_store_good_id']  # 添加购买数量
    request.session['store_send_number'] = int(request.POST['send_number'])  # 添加购买数量
    store_good = Store.objects.get(id=request.session['send_store_good_id'])
    request.session['store_good_price'] = store_good.price

    good = Goods.objects.get(id=store_good.good_id)
    request.session['store_send_good_desc'] = good.descr
    request.session['store_send_good_name'] = good.goods
    return render(request, 'myweb/store_send.html')

# 库存-发货表单
def store_xd(request):

    # 库存不足的判断还没写

    store_good_id = request.session['send_store_good_id']
    store_good_send_num = request.session['store_send_number']
    store_good = Store.objects.get(id=store_good_id)
    store_good.number = store_good.number - store_good_send_num

    store_good.save()

    dispatch = Dispatch()
    dispatch.uid = store_good.uid
    dispatch.good_id = store_good.good_id
    dispatch.store_id = store_good.id
    dispatch.linkman  = request.POST['linkman']
    dispatch.phone = request.POST['phone']
    dispatch.address = request.POST['address']
    dispatch.code = request.POST['code']
    dispatch.number = request.session['store_send_number']
    dispatch.status = 0
    dispatch.addtime = time.time()
    dispatch.save()

    return redirect(reverse('store_order'))
