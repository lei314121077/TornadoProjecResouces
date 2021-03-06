#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '锦峰'

import tornado.web, meta, auth
import xml.etree.ElementTree as ET
from db import Mysqldb, log
import time, datetime


 #获得所有MP列表
#class MPListHandler(tornado.web.RequestHandler):
    #__metaclass__ = meta.HandlerMetaClass
    #route = r'/mymp'

    #def get_current_user(self):
        #return self.get_secure_cookie('username')

    #@auth.authenticated
    #def get(self):
        #dao = MPSiteDao()
        #root = ET.Element('mplist')
        #for s in dao.get_all_sites_by_username(self.get_current_user()):
            #id, token, name, ghid, appid, secret, validated, validate_time, enabled, user_id, username  = s
            #mp = ET.SubElement(root, 'mp', id=str(id))
            #self.__append_element(mp, 'token', token)
            #self.__append_element(mp, 'name', name)
            #self.__append_element(mp, 'ghid', ghid)
            #self.__append_element(mp, 'appid', appid)
            #self.__append_element(mp, 'secret', secret)
            #self.__append_element(mp, 'validated', str(validated))
            #self.__append_element(mp, 'validate-time', str(int(time.mktime(validate_time.timetuple())) if validate_time is not None else 0))
            #self.__append_element(mp, 'enabled', str(enabled))
            #user_elm = ET.SubElement(mp, 'user', id=str(user_id))
            #username_elm = ET.SubElement(user_elm, 'username')
            #username_elm.text = username
        #self.set_header('Content-Type', 'text/xml; charset=utf-8')
        #self.write(ET.tostring(root, encoding='UTF-8'))

    #def __append_element(self, parent, tag, value):
        #e = ET.Element(tag)
        #if value is not None:
            #e.text = value
        #parent.append(e)

#class MPHandler(tornado.web.RequestHandler):
    #__metaclass__ = meta.HandlerMetaClass
    #route = r'/mp/(.*)'

    #def get_current_user(self):
        #return self.get_secure_cookie('username')

    #@auth.authenticated
    #def put(self, mpid):
        ## 修改
        #dao = MPSiteDao()
        #if not dao.own(self.get_current_user(), int(mpid)):
            #self.send_error(401)
        #else:
            #root = ET.fromstring(self.request.body)
            #token = root.findtext('token')
            #name = root.findtext('name')
            #ghid = root.findtext('ghid')
            #appid = root.findtext('appid')
            #secret = root.findtext('secret')
            #enabled = int(root.findtext('enabled') or '0')
            #dao.update(mpid, token, name, ghid, appid, secret, enabled)
            #self.set_header('Content-Type', 'text/xml; charset=utf-8')
            #self.write('<mp id="%s"/>' % mpid)

    #@auth.authenticated
    #def delete(self, mpid):
        ## 删除
        #try:
            #dao = MPSiteDao()
            #if not dao.own(self.get_current_user(), int(mpid)):
                #self.send_error(401)
            #else:
                #dao.delete(mpid)
                #self.set_header('Content-Type', 'text/xml; charset=utf-8')
                #self.write('<mp id="%s"/>' % mpid)
        #except:
            #self.send_error(500)

#class MPHandler(tornado.web.RequestHandler):
    #__metaclass__ = meta.HandlerMetaClass
    #route = r'/mp'

    #def get_current_user(self):
        #return self.get_secure_cookie('username')

    #@auth.authenticated
    #def post(self):
        ## 新增
        #dao = MPSiteDao()
        #root = ET.fromstring(self.request.body)
        #token = root.findtext('token')
        #name = root.findtext('name')
        #ghid = root.findtext('ghid')
        #appid = root.findtext('appid')
        #secret = root.findtext('secret')
        #mpid = dao.add(self.get_current_user(), token, name, ghid, appid, secret)
        #self.set_header('Content-Type', 'text/xml; charset=utf-8')
        #self.write('<mp id="%s"/>' % mpid)

class MPSite(object):
    def __init__(self, wxtoken):
        self.dao = MPSiteDao()
        self.wxtoken = wxtoken
        self.id, self.name, self.ghid, self.appid, self.secret, self.validated, self.validateTime, self.enabled = \
            self.dao.get_by_token(wxtoken) or (None, None, None, None, None, None, None, None)

    def access(self):
        self.dao.create(self.wxtoken)

    def close(self):
        self.dao.close()

class MPSiteDao(object):
    def __init__(self):
        self.db = Mysqldb()
        self.__create_table(self.db)

    def __create_table(self, db):
        db.execute('''
            CREATE TABLE IF NOT EXISTS weicbd_mp_site (
                id bigint NOT NULL AUTO_INCREMENT,
                user_id bigint NOT NULL,
                token varchar(32) NOT NULL,
                name varchar(255) DEFAULT NULL,
                ghid varchar(255) DEFAULT NULL,
                appid varchar(255) DEFAULT NULL,
                secret varchar(255) DEFAULT NULL,
                validated boolean DEFAULT FALSE,
                validateTime timestamp DEFAULT 0,
                enabled boolean DEFAULT TRUE,

                PRIMARY KEY (id),
                FOREIGN KEY(user_id) REFERENCES weicbd_account(id),
                UNIQUE KEY (token)
            ) DEFAULT CHARACTER SET=utf8;
        ''')

    def close(self):
        self.db.commit()

    def access(self, token):
        n, = self.db.fetchone('SELECT COUNT(id) FROM weicbd_mp_site WHERE token=%s', (token, ))
        if n == 1:
            self.db.execute('UPDATE weicbd_mp_site SET validated=%s, validateTime=%s WHERE token=%s', (True, datetime.datetime.now(), token))
            self.db.commit()
            return True
        else:
            return False

    def get_by_token(self, wxtoken):
        return self.db.fetchone('''
            SELECT id, name, ghid, appid, secret, validated, validateTime, enabled FROM weicbd_mp_site WHERE token=%s
            ''', (wxtoken, ))

    def create(self, wxtoken):
        self.db.execute('INSERT IGNORE INTO weicbd_mp_site(token) VALUES(%s)', (wxtoken, ))
        
    def get_all_sites(self):
        return self.db.fetchall('SELECT id, token, name, ghid, appid, secret, validated, validateTime, enabled FROM weicbd_mp_site')
        
    def update_sites(self, id, name, ghid, appid, secret, enabled):
        self.db.execute('UPDATE weicbd_mp_site SET name=%s, ghid=%s, appid=%s, secret=%s, enabled=%s WHERE id=%s',
            (name, ghid, appid, secret, enabled, id))
        self.db.commit()

    def get_all_sites_by_username(self, username):
        role, = self.db.fetchone('SELECT r.role FROM weicbd_role r, weicbd_account u WHERE u.role_id=r.id AND u.username=%s', (username,))
        if role == 'admin':
            return self.db.fetchall('''
                SELECT m.id, m.token, m.name, m.ghid, m.appid, m.secret, m.validated, m.validateTime, m.enabled, u.id, u.username
                FROM weicbd_mp_site m, weicbd_account u
                WHERE m.user_id=u.id
            ''')
        else:
            return self.db.fetchall('''
                SELECT m.id, m.token, m.name, m.ghid, m.appid, m.secret, m.validated, m.validateTime, m.enabled, u.id, u.username
                FROM weicbd_mp_site m, weicbd_account u
                WHERE m.user_id=u.id AND u.username=%s
            ''', (username,))

    def own(self, username, mpid):
        r, = self.db.fetchone('''
            SELECT COUNT(u.id) FROM weicbd_account u, weicbd_role r WHERE u.role_id=u.id AND u.username=%s AND r.role=%s
        ''', (username, 'admin'))
        if r == 1:
            return True
        n, = self.db.fetchone('''
            SELECT COUNT(m.id) FROM weicbd_account u, weicbd_mp_site m WHERE m.user_id=u.id AND u.username=%s AND m.id=%s
        ''', (username, mpid))
        return n == 1

    def update(self, mpid, token, name, ghid, appid, secret, enabled):
        rt = self.db.execute('UPDATE weicbd_mp_site SET token=%s, name=%s, ghid=%s, appid=%s, secret=%s, enabled=%s WHERE id=%s',
                             (token, name, ghid, appid, secret, enabled, mpid))
        self.db.commit()
        return rt

    def delete(self, mpid):
        rt = self.db.execute('DELETE FROM  weicbd_mp_site WHERE id=%s',
                             (mpid,))
        self.db.commit()
        return rt

    def add(self, username, token, name, ghid, appid, secret):
        rt = self.db.execute('INSERT INTO weicbd_mp_site(token, name, ghid, appid, secret, user_id) SELECT %s, %s, %s, %s, %s, id FROM weicbd_account WHERE username=%s',
                             (token, name, ghid, appid, secret, username))
        self.db.commit()
        return rt

        

