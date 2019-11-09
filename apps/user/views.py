from django.shortcuts import render
import logging
# 生成一个以当前文件名为名字的logger实例
logger = logging.getLogger(__name__)

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework import permissions,authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from random import choice
# Create your views here.
from .serializers import SmsSerializer,UserRegSerializer,UserDetailSerializer
from .models import VerifyCode
from utils.yunpian import YunPian
from backend.settings import APIKEY


User = get_user_model()

class CustomBackend(ModelBackend):
    """
    用户自定义验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(mixins.CreateModelMixin,GenericViewSet):
    """
    发送短信验证码
    """

    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成6位数字验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]
        yun_pian = YunPian(APIKEY)
        code = self.generate_code()
        sms_status = yun_pian.send_sms(code=code,mobile=mobile)
        logger.info("用户注册验证码云片网返回请求结果:" +str(sms_status))
        if sms_status["code"] != 0:
            return Response(
                {
                    "mobile":sms_status["msg"]
                },status=status.HTTP_400_BAD_REQUEST
            )
        else:
            code_record = VerifyCode(code=code,mobile=mobile)
            code_record.save()
            return Response(
                {"mobile":mobile},status=status.HTTP_201_CREATED
            )

class UserViewset(mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,GenericViewSet):
    """
    用户注册
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()

    authentication_classes = (JSONWebTokenAuthentication,authentication.SessionAuthentication)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return  UserRegSerializer

        return UserDetailSerializer

    # permission_classes = (permissions.IsAuthenticated,)
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []
        return []
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username


        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()
