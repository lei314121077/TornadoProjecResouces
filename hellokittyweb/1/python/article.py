﻿#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '北极鱼'

import tornado.web, meta
from orm import getSession
import xml.etree.ElementTree as ET
from model.articleobj import Article, Comment, Password
import time, datetime
from db import Mysqldb, log

class ArticleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/article'

    # 新增博客
    def post(self):
        pas = self.get_cookie('getpassword')
        root = ET.fromstring(self.request.body)
        title = root.find('title').text
        content = root.find('content').text
        atime = datetime.date.today()          # 拿到当前日期
        tag = root.find('tag').text
        priority = root.find('priority').text
        session = getSession()
        aa = Article(title, content, atime, priority, tag)
        if pas:
            session.add(aa)
            session.commit()
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<article id="%d"/>' % aa.id)
        else:
            self.send_error(401)

class AllArticleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/articles'

    #列出所有博客
    def get(self):
        root = ET.Element('articles')   # 设置根节点
        session = getSession()
        pagesize = int(self.get_argument('pagesize',10))
        pagenumber = int(self.get_argument('pagenumber',0))
        a = session.query(Article).offset(pagesize*pagenumber).limit(pagesize)
        if a:
            for val in a:
                art = ET.SubElement(root, 'article')
                art.attrib['id'] = str(val.id)       # 设置根节点属性
                art.attrib['pid'] = str(val.priority)
                ET.SubElement(art, 'title').text = val.title
                ET.SubElement(art, 'atime').text = str(val.atime)
                ET.SubElement(art, 'tag').text = val.tag
                ET.SubElement(art, 'content').text = val.content
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

class ArticlesHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/article/(.*)'
    # 列某篇博客
    def get(self, aid):
        root = ET.Element('articles')   # 设置根节点
        atid = int(aid)
        session = getSession()
        a = session.query(Article).filter(Article.id == atid).first()
        if a:
            art =  ET.SubElement(root, 'article')
            art.attrib['id'] = str(a.id)       # 设置根节点属性
            art.attrib['pid'] = str(a.priority)       # 设置根节点属性
            ET.SubElement(art, 'title').text = a.title
            ET.SubElement(art, 'atime').text = str(a.atime)
            ET.SubElement(art, 'content').text = a.content
            ET.SubElement(art, 'tag').text = a.tag
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    # 更新博客
    def put(self, id):

        pas = self.get_cookie('getpassword')
        root = ET.fromstring(self.request.body)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        aid = int(id)
        session = getSession()
        atrcle = session.query(Article).filter(Article.id == aid).first()
        if atrcle and pas:
            atrcle.title = root.find('title').text
            atrcle.priority = root.get('pid')
            atrcle.content = root.find('content').text
            atrcle.tag = root.find('tag').text
            session.merge(atrcle)
            session.commit()
            self.write('<article id="%s"/>' %int(atrcle.id))
        else:
            self.send_error(401)

    # 删除博客
    def delete(self, id):

        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        pas = self.get_cookie('getpassword')
        aid = int(id)
        session = getSession()
        aa = session.query(Article).filter(Article.id == aid).first()
        if aa and pas:
            session.delete(aa)
            session.commit()
            self.write('<article id="%s"/>'% int(aid))
        else:
            self.send_error(401)

class LatelyArticleHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/latelyarticle'

    # 找出最新的十条博客
    def get(self):
        root = ET.Element('articles')   # 设置根节点
        session = getSession()
        aa = session.query(Article).order_by(Article.id).offset(0).limit(10)      #  offset(0).limit(10).order_by(desc=True)

        if aa:
            for val in aa:
                art = ET.SubElement(root, 'article')
                art.attrib['id'] = str(val.id)       # 设置根节点属性
                art.attrib['pid'] = str(val.priority)
                ET.SubElement(art, 'title').text = val.title
                ET.SubElement(art, 'atime').text = str(val.atime)
                ET.SubElement(art, 'tag').text = val.tag
                ET.SubElement(art, 'content').text = val.content[0:200]
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))


class LatelyCommentsHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/latelycomments'

    # 找出最新的十条评论
    def get(self):
        root = ET.Element('comments')   # 设置根节点
        session = getSession()
        cc = session.query(Comment).order_by(Comment.id).offset(0).limit(10)       #offset(0).limit(10).order_by(desc=True)
        if cc:
            for val in cc:
                com = ET.SubElement(root, 'comment')
                com.attrib['id'] = str(val.id)
                com.attrib['aid'] = str(val.article_id)
                ET.SubElement(com, 'email').text = self.acess_email(val.email)
                ET.SubElement(com, 'content').text = val.content
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    # 处理邮箱
    def acess_email(self, email):
        length = email.find('@')
        number = email[3:length]
        return email.replace(number, '***')

class CommentHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/comments'

    # 评论
    def post(self):
        root = ET.fromstring(self.request.body)
        articleid = int(root.get('articleid'))
        email = root.find('email').text
        content = root.find('content').text
        session = getSession()
        cc = Comment(articleid, content, email)
        session.add(cc)
        session.commit()
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<comment id="%s"/>'% int(cc.id))


class CommentsHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/comments/(.*)'

    # 某篇文章的评论
    def get(self, id):
        root = ET.Element('comments')   # 设置根节点
        aid = int(id)
        session = getSession()
        pagesize = int(self.get_argument('pagesize', 10))
        pagenumber = int(self.get_argument('pagenumber', 0))
        cc = session.query(Comment).filter(Comment.article_id == aid).order_by(Comment.id).offset(pagesize*pagenumber).limit(pagesize)
        for val in cc:
            com = ET.SubElement(root, 'comment')
            com.attrib['id'] = str(val.id)
            com.attrib['aid'] = str(val.article_id)
            ET.SubElement(com, 'email').text = self.acess_email(val.email)
            ET.SubElement(com, 'content').text = val.content

        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    # 删评论
    def delete(self, id):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        pas = self.get_cookie('getpassword')
        cid = int(id)
        session = getSession()
        cc = session.query(Comment).filter(Comment.id == cid).first()
        if cc and pas:
            session.delete(cc)
            session.commit()
            self.write('<article id="%s"/>'% int(cid))
        else:
            self.send_error(401)

    # 处理邮箱
    def acess_email(self, email):
        length = email.find('@')
        number = email[3:length]
        return email.replace(number, '******')

class PasswordHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/password'

    def post(self):
         root = ET.fromstring(self.request.body)
         password = root.find('password').text
         session = getSession()
         passw = session.query(Password).filter(Password.id == 1).all()
         if passw:
             self.set_secure_cookie('getpassword',password)           # 放入会话（Cookie）

    # 改密码
    def put(self):
        pas = self.get_cookie('getpassword')
        root = ET.fromstring(self.request.body)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        session = getSession()
        pw = session.query(Password).filter(Password.id == 1).first()
        if pw and pas:
            pw.password = root.find('password').text
            session.merge(pw)
            session.commit()
            self.write('<password id="%s"/>' %int(pw.id))

    # 加账户密码
    # def post(self):
    #     root = ET.fromstring(self.request.body)
    #     password = root.find('password').text
    #     session = getSession()
    #     if password:
    #         pp = Password(password)
    #         session.add(pp)
    #         session.commit()

class ArticlePageHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/articlecount'
    # 拿到博客总记录数
    def get(self):
        session = getSession()
        aa = session.query(Article).count()     # 拿到博客的总记录数
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<count>%s</count>' %int(aa))

class CommentPageHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/commentcount/(.*)'

    # 拿到评论总记录数
    def get(self, aid):
        session = getSession()
        aa = session.query(Comment).filter(Comment.article_id == int(aid)).count() # 拿到博客的总记录数
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<count>%s</count>' %int(aa))






