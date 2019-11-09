#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/9 15:18
# @Author  : qinmin
# @File    : serializers.py
import re
from datetime import datetime,timedelta
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import  get_user_model

from backend.settings import REGEX_MOBILE
from .models import VerifyCode
User = get_user_model()

class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)
    def validate_mobile(self,mobile):
        """
        验证手机号码
        :param mobile:
        :return:
        """
        #手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经注册")

        #验证手机号码是否合法
        if not re.match(REGEX_MOBILE,mobile):
            raise serializers.ValidationError("手机号码非法")

        #限制验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0,minutes=1,seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago,mobile=mobile).count():
            raise serializers.ValidationError("请求过于频繁，请稍后再试")

        return  mobile

class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    class Meta:
        model = User
        fields = ("name","gender","birthday","email","mobile")

class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True,write_only=True,max_length=6,min_length=6,label="验证码",
                                 error_messages={
                                     "blank":"请输入验证码",
                                     "required":"请输入验证码",
                                     "max_length":"验证码格式错误",
                                     "min_length":"验证码格式错误"
                                 },help_text="验证码")

    username = serializers.CharField(label="用户名",help_text="用户名",required=True,allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(),message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type':'password'},help_text="密码",label="密码",write_only=True
    )

    def create(self, validated_data):
        user = super(UserRegSerializer,self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validated_code(self,code):
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0,minutes=5,seconds=0)
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username","code","mobile","password")