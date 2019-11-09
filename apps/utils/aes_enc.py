#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/15 16:27
# @Author  : qinmin
# @File    : aes_enc.py

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

url="http://pcc.iread.wo.com.cn/registerlogin/rest/register/temp/enecrypt"
# 如果text不足16位的倍数就用空格补足为16位
def add_to_16(text):
    if len(text.encode('utf-8')) % 16:
        add = 16 - (len(text.encode('utf-8')) % 16)
    else:
        add = 0
    text = text + ('\0' * add)
    return text.encode('utf-8')


# 加密函数
def encrypt_cbc(text):
    key = 'update!@#1234567'.encode('utf-8')
    mode = AES.MODE_CBC
    iv = b'16-Bytes--String'
    text = add_to_16(text)
    cryptos = AES.new(key, mode, iv)
    cipher_text = cryptos.encrypt(text)
    # 因为AES加密后的字符串不一定是ascii字符集的，输出保存可能存在问题，所以这里转为16进制字符串
    return b2a_hex(cipher_text)


# 加密函数
def encrypt_ebc(text):
    key = 'update!@#1234567'.encode('utf-8')
    mode = AES.MODE_ECB
    text = add_to_16(text)
    cryptos = AES.new(key, mode)

    cipher_text = cryptos.encrypt(text)
    return b2a_hex(cipher_text)


if __name__ == '__main__':
    e = encrypt_cbc("13373182309")  # 加密
    # d = decrypt(e)  # 解密
    print("加密:", e)
    # print("解密:", d)