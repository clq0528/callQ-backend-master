#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 17:57
# @Author  : qinmin
# @File    : adminx.py
import xadmin

from .models import ShoppingCart,OrderInfo,OrderGoods

class ShoppingCartAdmin(object):
    list_display = ["user","goods","nums"]

class OrderInfoAdmin(object):
    list_display = ["user","order_sn","trade_no","pay_status","post_script","order_mount","pay_time","add_time"]

    class OrderGoodInline(object):
        model = OrderGoods
        exclude = ["add_time",]
        extra = 1
        style = "tab"

    inlines = [OrderGoodInline,]

xadmin.site.register(ShoppingCart,ShoppingCartAdmin)
xadmin.site.register(OrderInfo,OrderInfoAdmin)


