#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '北极鱼'

import tornado.web, meta, auth,  random
import xml.etree.ElementTree as ET
from db import Mysqldb, log
from weicbd.mpmember import UserDao

class RegisterHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/regmember'
    def post(self):
        dao = UserDao()
        root = ET.fromstring(self.request.body)
        mobile = root.find('mobile').text
        vcode = root.find('vcode').text
        emai = root.find('email').text
        name = root.find('name').text
        password = root.find('password').text
        sex = root.find('sex').text
        birth = root.find('birth').text
        if mobile is not None:
            dao.user_register(mobile, vcode, emai, name, sex, birth, password)
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<member/>')

class LoginHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/logmember'
    def post(self):
        dao = UserDao()
        root = ET.fromstring(self.request.body)
        mobile = root.find('mobile').text
        password = root.find('password').text
        result = dao.user_login(mobile, password)
        if result is not None:
            self.set_secure_cookie('mobile', mobile)
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<member/>')

class ValidateCodeHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/vcodemember'
    def post(self):
        dao = UserDao()
        root = ET.fromstring(self.request.body)
        mobile = root.find('mobile').text
        vcode = random.randint(1000, 9999)     # 随机生成4个整数字符串 这里开始接入手机接口
        res = dao.insert_vcode(mobile, vcode)
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<member/>')
            self.set_cookie('mobile', mobile)

class LogoutMemberHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/mplogout'
    def post(self):
        self.clear_cookie('mobile')
















