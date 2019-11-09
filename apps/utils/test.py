#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/16 8:55
# @Author  : qinmin
# @File    : test.py

import sentry_sdk
sentry_sdk.init("http://79e4d3d871d94b6ea0741faf746cae3b@47.106.193.103:9000/2")

class test():
    def _name(names):
        print('print name'+names)



test._name('hello')


class Desc:
  def __get__(self, ins, cls):
    print('self in Desc: %s ' % self )
    print(self, ins, cls)
class Test:
  x = Desc()
  def prt(self):
    print('self in Test: %s' % self)
t = Test()
t.prt()
t.x
