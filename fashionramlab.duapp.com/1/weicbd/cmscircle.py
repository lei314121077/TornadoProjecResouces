#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '北极鱼'

import tornado.web, meta, auth
import xml.etree.ElementTree as ET
from db import Mysqldb, log

# 创建圈子
class CreateCircleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/createcircle'
    def post(self):

        dao = CircleDao()
        root = ET.fromstring(self.request.body)
        name = root.find('name').text
        depict = root.find('depict').text
        res = dao.create_circle(name, self.get_secure_cookie('mobile'), depict)
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<member id="%s"/>'% int(res))
        else:
            self.send_error(401)
# 添加角色
class AddRoleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route =r'/mod/cms/addrole'
    def post(self):

        dao = CircleDao()
        root = ET.fromstring(self.request.body)
        rolename = root.find('rolename').text
        circleid = root.find('circleid').text
        res = dao.create_role(self.get_secure_cookie('mobile'),circleid,rolename)
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<roles id="%s"/>'% int(res))
        else:
            self.send_error(401)

# 添加圈子
class AddCircleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/addcircle'
    def post(self):

        dao = CircleDao()
        root = ET.fromstring(self.request.body)
        circleid = root.find('circleid').text                           # 要添加的圈子
        res = dao.add_circle(circleid, self.get_secure_cookie('mobile'))
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<circles id="%s"/>'% int(res))
        else:
            self.send_error(401)

# 为成员分配角色
class PutMemberRoleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/putmemberrole/(.*)'
    def put(self,cid):
        dao = CircleDao()
        root = ET.fromstring(self.request.body)
        roleid = root.find('roleid').text
        memberid = root.find('memberid').text
        dao.update_member_role(self.get_secure_cookie('mobile'), memberid, roleid, cid)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<roles id="'+roleid+'"/>')

# 修改角色
class PutRoleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/putrole/(.*)'
    def put(self,cid):
        dao = CircleDao()
        root = ET.fromstring(self.request.body)
        rolename = root.find('role').text
        roleid = root.find('roleid').text
        res = dao.update_role(self.get_secure_cookie('mobile'), rolename, roleid,cid)
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<roles id="'+res+'"/>')
        else:
            self.send_error(401)


# 删除角色
class RemoveRoleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/removerole/(.*)'
    def delete(self, roleid):
        dao = CircleDao()
        dao.reomeve_role(roleid)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<roles id="'+roleid+'"/>')
# 退出圈子
class ExitCircleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/cms/exitcircle/(.*)'
    def delete(self,cid):
        dao = CircleDao()
        dao.exit_circle(self.get_secure_cookie('mobile'),cid)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<circles id="'+cid+'"/>')

# 踢出成员
class ExitMemberHandler(tornado.web.RequestHandler):
    __metaclass__=meta.HandlerMetaClass
    route =r'/mod/cms/exitmember/(.*)'
    def delete(self, memberid):
        dao = CircleDao()
        dao.exit_member(self.get_secure_cookie('mobile'),memberid)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<members id="'+memberid+'"/>')

#  搜索当前圈子成员列表
class CircleMemberListHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route =r'/mod/cms/memberlist/(.*)'
    def get(self,cid):
        dao = CircleDao()
        root = ET.Element('member_list')   # 设置根节点
        for res in dao.query_circles_list(self.get_secure_cookie('mobile'),cid) or []:
            id, name, role, rid, circle, cid = res
            mess = ET.SubElement(root, 'members', {'id': str(id)}) # 设置子节点 属性值
            self.__append_element(mess, 'name', name)
            self.__append_element(mess, 'role', role, {'id': str(rid)})
            self.__append_element(mess, 'circle', circle, {'id': str(cid)})

        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value, val=None):
        e = ET.Element(tag)
        if value:
            if val is not None:         #   如果第四个参数不为空
                e = ET.SubElement(e, tag, val) # 设置属性节点
            e.text = value
        parent.append(e)



#   检索角色列表
class RoleListHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route =r'/mod/cms/rolelist/(.*)'
    def get(self,cid):
        dao = CircleDao()
        root = ET.Element('role_list')   # 设置根节点
        for res in dao.query_role_list(cid):
            id, name, circle, cid = res
            mess = ET.SubElement(root, 'roles', {'id':str(id)})    # 设置子节点 属性值
            self.__append_element(mess, 'name', name)
            self.__append_element(mess, 'circle', circle, {'id':str(cid)})
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value, val=None):
        e = ET.Element(tag)
        if value:
            if val is not None:         #   如果第四个参数不为空
                e = ET.SubElement(e, tag, val) # 设置属性节点
            e.text = value
        parent.append(e)

#  检索所有圈子
class AllCircleHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/mod/cms/allcircle'
    def get(self):
        dao = CircleDao()
        root = ET.Element('circle_list')  # 设置根节点
        for res in dao.query_all_circle() or []:
            id, name, depict = res
            mess = ET.SubElement(root, 'circles', {'id':str(id)})   # 设置子节点和属性值
            self.__append_element(mess, 'name', name)
            self.__append_element(mess, 'depict', depict)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)

 # 按名称搜索圈子
class QueryCircleNameHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/mod/cms/namecircle'
    def post(self):
        dao = CircleDao()
        rot = ET.fromstring(self.request.body)
        name =rot.find('name').text
        root = ET.Element('circle_list')
        for res in dao.query_circle_name(name) or []:
            id, name, depict = res
            mess = ET.SubElement(root, 'circles', {'id':str(id)})   # 设置子节点和属性值
            self.__append_element(mess, 'name', name)
            self.__append_element(mess, 'depict', depict)
        self.set_header('Content-Type', 'text/xml: charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)

# 找出当前帐号所在的圈子
class QueryMemberHandler(tornado.web.RequestHandler):
    __metaclass__=meta.HandlerMetaClass
    route = r'/mod/cms/membercircle'
    def get(self):
        dao = CircleDao()
        root = ET.Element('circle_list')
        for res in dao.query_member_circle(self.get_secure_cookie('mobile')) or []:
            id,  name, depict =res
            mess = ET.SubElement(root, 'circles', {'id':str(id)})   # 设置子节点和属性值
            self.__append_element(mess, 'name', name)
            self.__append_element(mess, 'depict', depict)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)

# 更新圈子
class UpdateCircleHandler(tornado.web.RequestHandler):
    __metaclass__=meta.HandlerMetaClass
    route = r'/mod/cms/updatecircle/(.*)'
    def put(self,id):
        dao = CircleDao()
        root = ET.fromstring(self.request.body)
        circlename = root.find('circlename').text
        depict = root.find('depict').text
        memberid = root.find('memberid').text
        res = dao.update_circle(id,circlename,depict,memberid)
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<circles id="'+id+'"/>')


class CircleDao(object):
    def __init__(self):
        self.db = Mysqldb()
        self.__create_table(self.db)

    def __create_table(self, db):
        #  圈子
        db.execute('''
                CREATE TABLE IF NOT EXISTS weicbd_mp_circle(
                id bigint NOT NULL AUTO_INCREMENT,
                memberid bigint NULL,
                name varchar(50) NOT NULL,
                depict varchar(80) NULL,
                FOREIGN KEY (memberid) REFERENCES weicbd_member(id),
                PRIMARY KEY (id)
                ) ''')

        # 角色
        db.execute('''
                CREATE TABLE IF NOT EXISTS weicbd_mp_role(
                id bigint NOT NULL AUTO_INCREMENT,
                name varchar(30) NOT NULL,
                circleid bigint NULL,
                FOREIGN KEY (circleid) REFERENCES weicbd_mp_circle(id),
                PRIMARY KEY (id)
                )
         ''')

        #  圈子成员
        db.execute('''
                CREATE TABLE IF NOT EXISTS weicbd_mp_circle_member(
                id bigint NOT NULL AUTO_INCREMENT,
                name varchar(50) NOT NULL,
                roleid  bigint NULL,
                circleid bigint NULL,
                memberid bigint NULL,
                FOREIGN KEY (circleid) REFERENCES weicbd_mp_circle(id),
                FOREIGN KEY (roleid) REFERENCES weicbd_mp_role(id),
                FOREIGN KEY (memberid) REFERENCES weicbd_member(id),
                PRIMARY KEY (id)
                )
         ''')
        db.commit()

    # 创建圈子
    def create_circle(self, name, member, depict):
        # 找到当前帐号的id
        memberid, = self.db.fetchone('select id from weicbd_member where mobile=%s',(member,)) or (None, )
        membername, = self.db.fetchone('select name from weicbd_member where mobile=%s',(member,)) or (None, )
        if memberid is not None:
            # 新建圈子成功返回圈子ID
            circleid = self.db.execute('insert into weicbd_mp_circle (name,memberid,depict) values(%s,%s,%s)', (name, memberid, depict)) or (None, )
            # 新建一个圈主的角色
            roleid = self.db.execute('insert into weicbd_mp_role (name,circleid) values("圈主",%s)',(circleid, )) or (None, )
            # 新建一个成员变量
            self.db.execute('insert into weicbd_mp_circle_member (name, roleid, circleid, memberid) values(%s, %s, %s, %s)', (membername, roleid, circleid, memberid)) or (None,)
            self.db.commit()
            return circleid

    # 添加圈子
    def add_circle(self, circleid, member):
        # 找到当前帐号的ID
        memberid, = self.db.fetchone('select id from weicbd_member where mobile=%s',(member,)) or (None, )
        # 找到当前账户的名称
        mname, = self.db.fetchone('select name from weicbd_member where mobile=%s',(member,)) or (None, )
        if (circleid is not None) and (memberid is not None):
            res = self.db.execute('insert into weicbd_mp_circle_member (name,circleid,memberid) values(%s,%s,%s) ',(mname,circleid,memberid))
            self.db.commit()
            return res

    # 退出圈子
    def exit_circle(self, mobile, cid):
        memberid, = self.db.fetchone('SELECT a.id FROM weicbd_mp_circle_member a, weicbd_mp_circle b, weicbd_member c WHERE a.circleid = b.id AND a.memberid = c.id AND a.circleid =%s AND c.mobile =%s ',(cid,mobile)) or (None, )
        if memberid is not None:
            self.db.execute('delete from weicbd_mp_circle_member where id=%s', (memberid,)) or (None, )
            self.db.commit()

    # 踢出成员
    def exit_member(self, mobile, memberid):
        role, = self.db.fetchone('SELECT a.name FROM weicbd_mp_role a, weicbd_mp_circle_member b, weicbd_member c WHERE a.id = b.roleid AND b.memberid = c.id AND c.mobile = %s', (mobile,)) or (None, )
        if role == '圈主':
            self.db.execute('delete from weicbd_mp_circle_member where id=%s', (memberid,))
            self.db.commit()

    # 创建角色
    def create_role(self, mobile, circleid, rname):
        role, = self.db.fetchone('SELECT a.name FROM weicbd_mp_role a, weicbd_mp_circle_member b, weicbd_member c WHERE a.id = b.roleid AND b.memberid = c.id AND c.mobile = %s', (mobile,)) or (None, )
        if role == '圈主':
            rid = self.db.execute('insert into weicbd_mp_role (name,circleid) values(%s,%s)',(rname,circleid)) or (None, )
            self.db.commit()
            return rid

    # 修改角色列表
    def update_role(self, mobile, name, roleid, cid):
        # 找到当前用户是否为圈主
        role, = self.db.fetchone('SELECT a.name FROM weicbd_mp_role a, weicbd_mp_circle_member b, weicbd_member c WHERE a.id = b.roleid AND b.memberid = c.id AND c.mobile = %s', (mobile,)) or (None, )
        if role == '圈主':
            self.db.execute('update weicbd_mp_role set name=%s where id = %s and circleid=%s ', (name, roleid, cid))
            self.db.commit()
            return roleid

    # 修改成员角色
    def update_member_role(self, mobile, memberid, roleid, cid):
        # 找到当前用户是否为圈主
        role, = self.db.fetchone('SELECT a.name FROM weicbd_mp_role a, weicbd_mp_circle_member b, weicbd_member c WHERE a.id = b.roleid AND b.memberid = c.id AND c.mobile = %s',(mobile,)) or (None, )
        if (role == '圈主') and (roleid is not None):
            self.db.execute('update weicbd_mp_circle_member set roleid=%s where id=%s and circleid=%s',(roleid, memberid, cid)) or (None, )
            self.db.commit()

    # 删除角色
    def reomeve_role(self, roleid):
        # 找到当前用户是否为圈主
        role, = self.db.fetchone('select a.roleid from weicbd_mp_circle_member a, weicbd_mp_role b where a.roleid=b.id  and b.id= %s',(roleid,)) or (None, )
        if role is None:
            self.db.execute('delete from weicbd_mp_role where id = %s',(roleid, )) or (None, )
            self.db.commit()

    # 圈子成员列表
    def query_circles_list(self, mobile, circleid):
        #当前帐号内是否存在该用户
        memberid, = self.db.fetchone('select a.memberid from weicbd_mp_circle_member a, weicbd_member b, weicbd_mp_circle c where a.memberid=b.id and a.circleid=c.id and c.id=%s and  b.mobile=%s',(circleid, mobile)) or (None, )
        if memberid is not None:
            # 查出当前圈子下的所有成员
            return self.db.fetchall('select a.id, a.name, b.name,b.id,c.name,c.id from weicbd_mp_circle_member a, weicbd_mp_role b, weicbd_mp_circle c where a.roleid=b.id and a.circleid=c.id and c.id=%s',(circleid,)) or (None, )

    # 角色列表
    def query_role_list(self, circleid):
        return self.db.fetchall('select a.id,a.name,b.name,b.id  from weicbd_mp_role a, weicbd_mp_circle b where a.circleid=b.id and b.id=%s',(circleid,)) or (None, )

    # 搜索全部圈子
    def query_all_circle(self):
        return self.db.fetchall('select id,name, depict from weicbd_mp_circle')

    # 按名称搜索圈子
    def query_circle_name(self, circlename):
        return self.db.fetchall('select id, name, depict from weicbd_mp_circle where name = %s', (circlename,)) or (None, )

    # 找出当前帐号所在的圈子
    def query_member_circle(self, mobile):
        return self.db.fetchall('select a.id, a.name, a.depict from weicbd_mp_circle a,weicbd_mp_circle_member b,weicbd_mp_member c where a.id=b.circleid and b.memberid=c.id and c.mobile=%s',(mobile,)) or []

    # 修改圈子
    def update_circle(self, id, name, depict, memberid):
        self.db.execute('update weicbd_mp_circle set name, depit, memberid  where id=%s',(name, depict, memberid, id)) or (None, )
        self.db.commit()
        return id























































