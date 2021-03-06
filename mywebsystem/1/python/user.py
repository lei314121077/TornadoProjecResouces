#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '北极鱼'

import tornado.web, meta, json
from orm import getSession
import xml.etree.ElementTree as ET
from model.usermodel import FlowerUser, FlowerUserType
import time, datetime
from db import Mysqldb, log
import sys

class UserHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/flower/user'

    # 添加用户类型
    def post(self):
        root = ET.fromstring(self.request.body)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        name = root.find("name").text
        password = root.find('password').text
        email = root.find('email').text
        mobile = root.find('mobile').text
        utype = root.find('utype').text
        session = getSession()
        user = FlowerUser(name, utype, email, mobile,password)
        if user:
            session.add(user)
            session.commit()
            self.write('<user id="%d"/>' % user.user_id)
        else:
            self.send_error(401)


    # 查看所有用户信息
    def get(self):
        root = ET.Element('users')
        session = getSession()
        user = session.query(FlowerUser).all()
        if user:
            for val in user:
                u = ET.SubElement(root, 'user')
                u.attrib['id'] =  str(val.user_id)
                u.attrib['tid'] = str(val.user_typeid)       # 设置根节点属性
                ET.SubElement(u, 'name').text = val.user_name
                ET.SubElement(u, 'email').text = str(val.user_email)
                ET.SubElement(u, 'mobile').text = str(val.user_mobile)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

class UsersHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/flower/user/(.*)'

    # 查看某个用户
    def get(self, id):
        root = ET.Element('users')
        session = getSession()
        user = session.query(FlowerUser).filter(FlowerUser.user_id == int(id))
        if user:
            for val in user:
                u = ET.SubElement(root, 'user')
                u.attrib['id'] =  str(val.user_id)
                u.attrib['tid'] = str(val.user_typeid)       # 设置根节点属性
                ET.SubElement(u, 'name').text = val.user_name
                ET.SubElement(u, 'email').text = str(val.user_email)
                ET.SubElement(u, 'mobile').text = str(val.user_mobile)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    # 修改用户
    def put(self, id):
        uid = int(id)
        root = ET.fromstring(self.request.body)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        session = getSession()
        cuser = self.get_cookie('getuser')

        user = session.query(FlowerUser).filter(FlowerUser.user_id == uid).first()
        if user :

            user.user_name = root.find('name').text
            user.user_email = root.find('email').text
            user.user_mobile = root.find('mobile').text
            user.user_password = root.find('password').text
            user.user_typeid = root.find('utype').text
            session.merge(user)
            session.commit()
            self.write('<user id="%s"/>' % int(user.user_id))


    # 删除用户
    def delete(self, id):
        uid = int(id)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        session = getSession()
        cuser = self.get_cookie('getuser')
        user = session.query(FlowerUser).filter(FlowerUser.user_id == uid).first()
        if user:
            session.delete(user)
            session.commit()
            self.write('<user id="%s"/>'% int(user.user_id))


class UserTypeHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/flower/usertype'

    # 添加用户类型
    def post(self):
        root = ET.fromstring(self.request.body)
        name = root.find('name').text
        session = getSession()
        utype = FlowerUserType(name)
        if utype:
            session.add(utype)
            session.commit()
            self.set_header('Content-Type', 'text/xml: charset=utf-8')
            self.write('<usertypes  id="%s"/>' % int(utype.utype_id))


    # 查看所有用户类型
    def get(self):
        root = ET.Element('usertypes')
        session = getSession()
        utype = session.query(FlowerUserType).all()

        if utype:
            for val in utype:
                ut = ET.SubElement(root, 'usertype')
                ut.attrib['tid'] = str(val.utype_id)       # 设置根节点属性
                ET.SubElement(ut, 'name').text = val.utype_name
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

class UserLoginHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/flower/login'

    # 登录用户
    def post(self):
        root = ET.fromstring(self.request.body)
        name = root.find('name').text
        password = root.find('password').text
        session = getSession()
        user = session.query(FlowerUser).filter(FlowerUser.user_name == name, FlowerUser.user_password == password).first()

        if user:
             list = (user.user_name, user.user_password, user.user_email, user.user_mobile) #生成元组放进会话
             self.set_secure_cookie('getuser',list)        # 放入会话（Cookie）













