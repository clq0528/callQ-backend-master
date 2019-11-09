#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/8 16:03
# @Author  : qinmin
# @File    : yunpian.py
import json
import requests
import logging
# 生成一个以当前文件名为名字的logger实例
logger = logging.getLogger(__name__)


class YunPian(object):
    def __init__(self,api_key):
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self,code,mobile):
        parmas = {
            "apikey":self.api_key,
            "mobile":mobile,
            "text":"【火树听书】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }

        response = requests.post(self.single_send_url,data=parmas)
        re_dict = json.loads(response.text)
        logger.info("云片网返回发送验证码请求结果情况-->" + str(re_dict))
        return re_dict

if __name__ == "__main__":
    yun_pian = YunPian("02378e9105cac5eeed5c400835269eb2")
    yun_pian.send_sms("2017","18974957679")