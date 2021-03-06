﻿#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web, meta, auth, random
import xml.etree.ElementTree as ET
from db import Mysqldb, log

class UserRegisterMemberHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mpregister'
    def post(self):
        dao = UserDao()
        root = ET.fromstring(self.request.body)
        mobile = root.find('mobile').text
        # vcode = root.find('vcode').text
        emai = root.find('email').text
        name = root.find('name').text
        password = root.find('password').text
        sex = root.find('sex').text
        birth = root.find('birth').text


        if mobile is not None:
            dao.user_register(mobile, emai, name, sex, birth, password, self.get_secure_cookie('ghid') , self.get_secure_cookie('openid'))
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<member/>')
    
class ValidateCodeHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mpvcode'
    def post(self):
        dao = UserDao()  
        root = ET.fromstring(self.request.body)
        mobile = root.find('mobile').text
        vcode = random.randint(1000,9999)        # 随机生成4个整数字符串 这里开始接入手机接口
        res = dao.insert_vcode(mobile,vcode)
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')           
            self.write('<member/>')
            self.set_cookie('mobile', mobile)
        
class LoginMemberHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mplogin'
    def post(self):
        dao = UserDao()
        root = ET.fromstring(self.request.body)
        mobile = root.find('mobile').text
        password = root.find('password').text      
        login = dao.user_login(mobile,password)
        if login is not None:
            self.set_cookie('mobile',mobile)
            self.set_header('Content-Type','text/xml; charset=utf-8')           
            self.write('<member/>')
        else:
            self.send_error(401)
def set_cookie(self,name,value):
    self.set_secure_cookie(name,value)
    
def get_cookie(self):
    return self.get_secure_cookie('mobile')


class PutMemberHandler(tornado.web.RequestHandler):      
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mpmember'      
    def put(self,mobile):
        dao = UserDao()
        root = ET.fromstring(self.request.body)
        mobile = self.get_secure_cookie('mobile')
        mail = root.find('email').text 
        name = root.find('name').text
        sex = root.find('sex').text
        password = root.find('password').text
        birth = root.find('birth').text
        dao.user_info(mail,name,sex,password,birth,mobile)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')           
        self.write('<member/>') 
                                 
class UserDao(object):
    
    def __init__(self):
        self.db = Mysqldb()
        self.__create_table(self.db)
                
    # 创建表    
    def __create_table(self,db): 
        db.execute('''
            CREATE TABLE IF NOT EXISTS weicbd_member (
                id bigint NOT NULL AUTO_INCREMENT,
                mobile varchar(20) NOT NULL,
                email varchar(30) NULL,
                name varchar(30) NULL,
                sex varchar(10) NULL,
                birth varchar(50)NULL,
                password varchar(30) NULL,
                
                constraint sex check (sex='男' or sex='女') ,
                
                PRIMARY KEY (id)
            ) DEFAULT CHARACTER SET=utf8;
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS weicbd_mp_vcode(
                id bigint NOT NULL AUTO_INCREMENT,
                mobile varchar(20) NOT NULL,
                vcode int NULL,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    
                PRIMARY KEY (id)
            ) DEFAULT CHARACTER SET=utf8;
        ''')
#        self.db.commit()

 
        
    # 用户注册
    def user_register(self, mobile, mail, name, sex, birth, password,ghid,openid):
        fmobile = self.db.fetchone('select id from weicbd_member where mobile =%s',(mobile,))
       # if fmobile == None:
       #    validate = self.db.fetchone('select * from weicbd_mp_vcode where mobile=%s and vcode=%s',(mobile,vcode))

        if fmobile is not None:
            self.db.execute('update weicbd_mp_member_rel set memberid=%s where ghid = %s and openid = %s',(fmobile, ghid, openid)) or (None, )
            self.db.commit()
        else:
            rt = self.db.execute('insert into weicbd_member (mobile,email,name,sex,birth,password) values(%s, %s, %s, %s, %s, %s)', (mobile, mail, name, sex, birth, password))
            self.db.commit()
            res, = self.db.fetchone('select id from weicbd_member where mobile=%s',(mobile, ))
            if res is not None:
                self.db.execute('update weicbd_mp_member_rel set memberid=%s where ghid = %s and openid = %s',(res, ghid, openid)) or (None, )
                self.db.commit()
                return rt
               
    # 用户登录      
    def user_login(self, mobile,password):
        return self.db.fetchone('select * from weicbd_member where mobile=%s and password=%s',(mobile,password))

    
    # 用户信息    
    def user_info(self, mail, name, sex, password, birth, mobile):
        minfo = self.db.fetchone('select mobile weicbd_mp_vcode where mobile=%s', (mobile,))
        if minfo is not None:
            self.db.execute('update weicbd_member set email=%s,name=%s,sex=%s,password=%s,birth=%s where mobile=%s',(mail, name, sex, password, birth, mobile))
            self.db.commit()
        else:
            self.send_error(401)       
                                
    # 验证码    
    def insert_vcode(self, mobile, vcode):
        fmobile = self.db.fetchone('select mobile from weicbd_member where mobile = %s', (mobile,))
        if fmobile == None:
           self.db.execute('insert into weicbd_mp_vcode (mobile,vcode) values(%s,%s)', (mobile, vcode))
           self.db.commit()
           
           
    
    
    
    