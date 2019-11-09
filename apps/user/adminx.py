#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 17:57
# @Author  : qinmin
# @File    : adminx.py
import xadmin
from xadmin import views
from .models import VerifyCode,UserImage

class BaseSeting(object):
    enable_themes = True
    use_bootswatch = True

class GlobalSettings(object):
    # 修改title
    site_title = '超市后台管理界面'
    # 修改footer
    site_footer = '太杂的杂货店'
    # 收起菜单
    menu_style = 'accordion'

class VerifyCodeAdmin(object):
    list_display = ["code","mobile","add_time"]

class UserImageAdmin(object):
    list_display = ["name","image","add_time"]

xadmin.site.register(VerifyCode,VerifyCodeAdmin)
xadmin.site.register(views.BaseAdminView,BaseSeting)
xadmin.site.register(views.CommAdminView,GlobalSettings)
xadmin.site.register(UserImage,UserImageAdmin)