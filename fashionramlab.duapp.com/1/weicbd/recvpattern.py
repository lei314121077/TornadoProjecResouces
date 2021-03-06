﻿#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web, meta, auth
import xml.etree.ElementTree as ET
from db import Mysqldb, log


class PatternListHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/recvpattern'

    def get_current_user(self):
        return self.get_secure_cookie('username') if self.get_secure_cookie('role') == 'admin' else None

    # 查出数据
    def get(self):
        dao = PatternDao()
        root = ET.Element('recv-patterns')   #设置根节点
        for res in dao.all_pattern():
            id, pattern, name = res
            rpet = ET.SubElement(root, 'recv-pattern', id=str(id)) #设置子节点
            self.__append_element(rpet, 'pattern', pattern) #设置pattern节点
            self.__append_element(rpet, 'name', name)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))


    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)

    @auth.authenticated
    def post(self):
        dao =PatternDao()
        self.set_header('Content-Type', 'text/xml; charset=utf-8')

        root = ET.fromstring(self.request.body)
        pattern =root.find('pattern').text
        name =root.find('name').text
        res =dao.add_pattern(pattern,name)
        self.write('<recv-pattern id = "%s"/>' % int(res))
         
class DeletePatternListHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/recvpattern/(.*)'

    def get_current_user(self):
        return self.get_secure_cookie('username') if self.get_secure_cookie('role') == 'admin' else None
            
    @auth.authenticated
    def delete(self,pid):
        dao =PatternDao()
        dao.del_pattern(int(pid))
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<recv-pattern id ="'+pid+'"/>' )
        
            
    @auth.authenticated
    def put(self,pid):
        dao =PatternDao()        
        root = ET.fromstring(self.request.body)
        pattern =root.find('pattern').text
        name =root.find('name').text    
        dao.put_pattern(pattern,name,pid)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<recv-pattern id = "%s"/>' % int(pid))
                    
class PatternDao(object):

    def __init__(self):
        self.db = Mysqldb()
        self.__create_table(self.db)

    #表
    def __create_table(self,db):
        db.execute('''
            CREATE TABLE IF NOT EXISTS  weicdb_recv_pattern(
            id bigint NOT NULL AUTO_INCREMENT,
            pattern varchar(515) not null,
            name varchar(255) not null,
            PRIMARY KEY (id)
            )''')

    # 查寻
    def all_pattern(self):
        return self.db.fetchall("select id,pattern,name from weicdb_recv_pattern")

    # 更新
    def put_pattern(self, pattern, name, pid):
        self.db.execute('update weicdb_recv_pattern set pattern = %s, name = %s where id = %s', (pattern, name, pid))
        self.db.commit()
        
    # 新建
    def add_pattern(self, pattern, name):
        pid = self.db.execute("insert into weicdb_recv_pattern(pattern,name) values(%s, %s)", (pattern, name))
        self.db.commit()
        return pid
        
    # 删除
    def del_pattern(self, pid):
        rt = self.db.execute("delete from weicdb_recv_pattern where id = %s", (pid,)) 
        self.db.commit()
        return rt
