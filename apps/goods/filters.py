#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/9/27 15:59
# @Author  : qinmin
# @File    : filters.py
from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Goods


class GoodsFilter(filters.FilterSet):
    pricemin = filters.NumberFilter(field_name="shop_price", lookup_expr='gte',help_text="最低价格")
    pricemax = filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    # name = filters.CharFilter(field_name="name",lookup_expr='icontains')
    top_category = filters.NumberFilter(method='top_category_filter')

    def top_category_filter(self,queryset,name,value):
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(category__parent_category__parent_category_id=value))
    class Meta:
        model = Goods
        fields = ['pricemin', 'pricemax','is_hot','is_new']


