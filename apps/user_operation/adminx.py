#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 17:57
# @Author  : qinmin
# @File    : adminx.py
import xadmin

from .models import UserFav,UserLeavingMessage,UserAddress

class UserFavAdmin(object):
    list_display = ["user","goods","add_time"]

class UserLeavingMessageAdmin(object):
    list_display = ["user","message_type","message","add_time"]

class UserAddressAdmin(object):
    list_display = ["signer_name","signer_mobile","district","address"]

xadmin.site.register(UserFav,UserFavAdmin)
xadmin.site.register(UserLeavingMessage,UserLeavingMessageAdmin)
xadmin.site.register(UserAddress,UserAddressAdmin)