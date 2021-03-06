#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '北极鱼'

import tornado.web, meta, auth
import xml.etree.ElementTree as ET
from db import Mysqldb, log

# 小商品列表
class ProductListHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/shop/productlist'
    def get(self):

        dao = ProductDao()
        root = ET.Element('products')   # 设置根节点
        for result in dao.all_products():
            id, name, price, store,  thumb, summary, status, priority, taglist_xml = result
            mess = ET.SubElement(root, 'product', {'id': str(id)})  # 设置子节点 属性值
            self.__append_element(mess, 'name', name)  # 设置孙节点
            self.__append_element(mess, 'price', str(price))        # 价格
            self.__append_element(mess, 'store', str(store))    # 库存
            self.__append_element(mess, 'thumb', thumb)   # 缩略图
            self.__append_element(mess, 'summary', summary)        # 概述
            self.__append_element(mess, 'status', status)       # 状态
            self.__append_element(mess, 'priority', str(priority))   # 优先级
            tags = ET.fromstring(taglist_xml.encode('utf-8'))
            mess.append(tags)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)

class FindProductHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/mod/shop/findproduct/(.*)'
    def get(self, id):
        dao = ProductDao()
        root = ET.Element('products')
        for res in dao.find_products(id):
            id, typename, name, price, store, description, thumb, spec, summary, status, image_xml, priority, taglist_xml = res
            mess = ET.SubElement(root, 'product', {'id': str(id)})
            self.__append_element(mess, 'typename', typename)
            self.__append_element(mess, 'name', name)
            self.__append_element(mess, 'price', str(price))
            self.__append_element(mess, 'store', str(store))
            self.__append_element(mess, 'description', description)
            self.__append_element(mess, 'thumb', thumb)
            self.__append_element(mess, 'spec', spec)
            self.__append_element(mess, 'summary', summary)
            self.__append_element(mess, 'status', status)
            self.__append_element(mess, 'proiority', str(property))
            if image_xml is not None:
                img = ET.fromstring(image_xml.encode('utf-8'))
                mess.append(img)
            if taglist_xml is not None:
                tags = ET.fromstring(taglist_xml.encode('utf-8'))
                mess.append(tags)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)

# 按标签检索商品
class QueryProductHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route =r'/mod/shop/queryproduct/(.*)'
    def get(self, queryid):
        dao = ProductDao()
        root = ET.Element('products')   # 设置根节点
        taglist = self.get_arguments('tag') or []         # 拿到get方法上URL传过来的标签

        for result in dao.query_products(taglist, queryid):
            id, name, price, store, description, summary, thumb, spec, taglist = result
            mess = ET.SubElement(root, 'product', {'id': str(id)})  # 设置子节点 属性值
            self.__append_element(mess, 'priority', name)  # 设置孙节点
            self.__append_element(mess, 'price', str(price))
            self.__append_element(mess, 'store', str(store))
            self.__append_element(mess,  'description', str(description))
            self.__append_element(mess, 'summary', summary)
            self.__append_element(mess, 'thumb', thumb)
            self.__append_element(mess, 'spec', spec)
            tagelement = ET.fromstring(taglist.encode('utf-8'))
            mess.append(tagelement)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)
# 创建商品类型
class AddProductTypeHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/shop/addproducttype'
    def post(self):
        dao = ProductDao()
        self.set_header('Content-Type', 'text/xml: charset=utf-8')
        root = ET.fromstring(self.request.body)
        name = root.find('name').text
        res = dao.create_type(name)
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<type id="%s"/>'% int(res))

class QueryProductTypeHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/mod/shop/querytype'
    def get(self):
        dao = ProductDao()
        root = ET.Element('types')   # 设置根节点

        for res in dao.query_type():
            id, name = res
            mess = ET.SubElement(root,'type',{'id':str(id)})
            self.__append_element(mess, 'name', name)

        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    def __append_element(self, parent, tag, value):
        e = ET.Element(tag)
        if value:
            e.text = value
        parent.append(e)
# 添加商品
class AddProductHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/mod/shop/addproduct'
    def post(self):
        dao = ProductDao()
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        root = ET.fromstring(self.request.body)
        name = root.find('name').text   # 名称
        price = root.find('price').text     # 价格
        store = root.find('store').text    # 库存
        description = root.find('description').text    # 描述
        summary = root.find('summary').text   # 概述
        thumb = root.find('thumb').text   # 缩略图
        spec = root.find('spec').text       # 规格
        status = root.find('status').text   # 状态
        priority = root.find('priority').text  # 优先级
        relid = root.find('relid').text   # 公众号
        images = root.find('images')    # 图片
        taglist = root.find('tags')        # 标签

        res = dao.add_products(name, price, store, description, summary, thumb, spec, status, priority, relid, ET.tostring(images, encoding='UTF-8', method="html"), ET.tostring(taglist, encoding='UTF-8', method="html"))
        if res is not None:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<products id="%s"/>'% int(res))

# 修改商品
class PutProductHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/mod/shop/putproduct/(.*)'
    def put(self, id):
        dao = ProductDao()
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        root = ET.fromstring(self.request.body)
        name = root.find('name').text
        price = root.find('price').text     # 价格
        store = root.find('store').text    # 库存
        description = root.find('description').text    # 描述
        summary = root.find('summary').text  # 概述
        thumb = root.find('thumb').text   # 缩略图
        spec = root.find('spec').text       # 规格
        status = root.find('status').text   # 状态
        priority = root.find('priority').text  # 优先级
        images = root.find('images')   # 图片
        dao.put_products(name, price, store, description, summary, thumb, spec, status, priority, ET.tostring(images, encoding='UTF-8', method="html"), id)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<products id="%s"/>' % int(id))

# 删除商品
class RemoveProductHandler(tornado.web.RequestHandler):
    __metaclass__= meta.HandlerMetaClass
    route = r'/mod/shop/removeproduct/(.*)'
    def delete(self,id):
        dao = ProductDao()
        res = dao.remove_product(id)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<products id="%s"/>' % int(res))

class ProductDao(object):

    def __init__(self):
        self.db = Mysqldb()
        self.__create_table(self.db)

    # 创建表
    def __create_table(self, db):
        # 商品
        db.execute('''
            CREATE TABLE IF NOT EXISTS weicbd_shopping_product(
                id bigint NOT NULL AUTO_INCREMENT,
                name varchar(50) null,
                price float null,
                store int null,
                description varchar(100) null,
                thumb text null,
                spec varchar(20) null,
                summary varchar(50) null,
                status varchar(50) null,
                image text null,
                priority int null,
                taglist text null,
                relid bigint  null,
                FOREIGN KEY (relid) REFERENCES weicbd_mp_member_rel(id),
                PRIMARY KEY (id)
            )DEFAULT CHARACTER SET=utf8;
        ''')

        # 订单
        db.execute('''
            create table if not exists weicbd_shopping_indent(
                id bigint not null auto_increment,
                memberid bigint null,
                consignee varchar(30) null,
                shippingAddress varchar(120) null,
                sendtime date null,
                number int null,
                meney float null,
                bigentime date null,
                status varchar(20) null,
                info varchar(35) null,
                FOREIGN KEY (memberid) REFERENCES weicbd_member(id),
                primary key (id)
            )DEFAULT CHARACTER SET=utf8;
        ''')



        # 收藏夹
        db.execute('''
            create table if not exists weicbd_shopping_favorite(
                id bigint not null auto_increment,
                productid bigint null,
                memberid bigint null,
                FOREIGN KEY (productid) REFERENCES weicbd_shopping_product(id),
                FOREIGN KEY (memberid) REFERENCES weicbd_member(id),
                primary key (id)
            )DEFAULT CHARACTER SET=utf8;
        ''')
        # 购物车
        db.execute('''
            create table if not exists weicbd_shopping_cart(
                id bigint not null auto_increment,
                memberid bigint null,
                productid bigint null,
                num int null,
                FOREIGN KEY (productid) REFERENCES weicbd_shopping_product(id),
                FOREIGN KEY (memberid) REFERENCES weicbd_member(id),
                primary key (id)
            )DEFAULT CHARACTER SET=utf8;
        ''')
        db.commit()

    # 新增商品
    def add_products(self, name, price, store, description, summary, thumb, spec, status, priority, relid, images, taglist):
        #result = self.db.fetchone('select spec from weicbd_shopping_product where spec=%s', (spec,))
        #if result is None:
        res = self.db.execute('insert into weicbd_shopping_product ( name, price, store, description, summary, thumb, spec, status, priority,relid, image, taglist) value(%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(name, price, store, description, summary, thumb, spec, status, priority, relid, images, taglist))
        self.db.commit()
        return res

    # 修改商品
    def put_products(self, name, price, store, description, summary, thumb, spec,  status, priority, images, id):
        self.db.execute('update weicbd_shopping_product set name=%s, price=%s, store=%s, description=%s, summary=%s, thumb=%s, spec=%s,  status=%s, priority=%s, image=%s where id=%s',( name, price, store, description, summary, thumb, spec, status, priority, images, id))
        self.db.commit()

    # 删除商品
    def remove_product(self, id):
        self.db.execute('delete from weicbd_shopping_product where id = %s',(id,))
        self.db.commit()
        return id

    # 小列表
    def all_products(self):
        return self.db.fetchall('select id, name, price, store,  thumb, summary, status, priority,taglist from weicbd_shopping_product')

    # 商品明细
    def find_products(self, id):
        return self.db.fetchall('select id,name,price,store,description,thumb,spec,summary,status,image,priority,taglist from weicbd_shopping_product  where a.id = %s',(id,))

    #  按标签查找商品列表
    def query_products(self, taglist, id):
        if taglist:
            substring = ' and '.join(['(count(/tags/tag[self:text()="%s"]) >=1)' % x for x in taglist])
            return self.db.fetchall('SELECT  id, name, price, store, description, summary, thumb, spec, taglist from weicbd_shopping_product where id in (select ft.id from (SELECT id, EXTRACTVALUE( taglist,\'%s\' ) as flag FROM weicbd_shopping_product) as ft where ft.flag=1) and id =%s'% (substring, id))
        else:
            return self.db.fetchall('select id,name,price,store,description,summary,thumb,spec,taglist from weicbd_shopping_product where id=%s',(id,))


