from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class UserProfile(AbstractUser):
    """
    用户表
    """
    name = models.CharField(max_length=30,null=True,blank=True,verbose_name="姓名")
    birthday = models.DateField(null=True,blank=True,verbose_name="出生年月")
    gender = models.CharField(max_length=6,choices=(("male",u"男"),("female","女")),default="female",verbose_name="性别")
    mobile = models.CharField(max_length=11,null=True,blank=True,verbose_name="电话")
    email =  models.CharField(max_length=100,null=True,blank=True,verbose_name="邮箱")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class VerifyCode(models.Model):
    """
    短信验证码
    """
    code = models.CharField(max_length=10,verbose_name="验证码")
    mobile = models.CharField(max_length=11,verbose_name="电话")
    add_time = models.DateTimeField(default=datetime.now,verbose_name="添加时间")

    class Meta:
        verbose_name = "短信验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code


#测试sftp文件上传
import os
from uuid import uuid4
class UserImage(models.Model):
    """
    User图
    """

    def path_and_rename(instance, filename):
        upload_to = 'user'
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(upload_to, filename)

    name = models.CharField(default='', max_length=20, verbose_name='名字')
    image = models.ImageField(upload_to=path_and_rename,verbose_name='图片',null=True,blank=True)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = '用户图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

