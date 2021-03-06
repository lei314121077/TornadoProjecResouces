# #! /usr/bin/env python
# # -*- coding: utf-8 -*-
#
# import tornado.web, meta, auth
# import xml.etree.ElementTree as ET
# from db import Mysqldb, log
#
#
# class EssayHandler(tornado.web.RequestHandler):
#     __metaclass__ = meta.HandlerMetaClass
#     route = r'/mparticle'
#
#     def post(self):
#         try:
#             dao = CmsArticleDao()
#             self.set_header('Content-Type', 'text/xml; charset=utf-8')
#             root = ET.fromstring(self.request.body)
#             mpid = int(root.get('mpid'))
#             priority = root.find('priority').text
#             title = root.find('title').text
#             content = root.find('content').text
#             summary = root.find('summary').text
#             thumb = root.find('thumb').text
#             taglist = root.find('tags')
#             images = ''.join(ET.tostringlist(root.find('images'), encoding='UTF-8')[1:])
#             if dao.validmp(self.get_secure_cookie('username'), mpid) or (self.get_secure_cookie('role') == 'admin'):
#                 res = dao.create_article(mpid, priority, title, content, summary, thumb, images, ET.tostring(taglist, encoding='UTF-8', method="html"))
#                 self.write('<article id="%s"/>' % str(res))
#             else:
#                 self.send_error(401)
#         except:
#             import traceback
#             log(traceback.format_exc())
#             self.send_error(500)
#
#
# class RemoveCmsArticleHandler(tornado.web.RequestHandler):
#     __metaclass__ = meta.HandlerMetaClass
#     route = r'/mparticle/(.*)'
#
#     def put(self, id):
#         try:
#             dao = CmsArticleDao()
#             self.set_header('Content-Type', 'text/xml; charset=utf-8')
#             root = ET.fromstring(self.request.body)
#             priority = root.find('priority').text
#             title = root.find('title').text
#             content = root.find('content').text
#             summary = root.find('summary').text
#             thumb = root.find('thumb').text
#             images = root.find('images')
#             trlgist = root.find('tags')
#             if dao.validptn(self.get_secure_cookie('username'), id) or (self.get_secure_cookie('role') == 'admin'):
#                 dao.update_article(priority, title, content, summary, thumb, ET.tostring(images, encoding='UTF-8', method="html"), ET.tostring(trlgist, encoding='UTF-8', method="html"), id)
#                 self.write('<article id="' + id + '"/>')
#             else:
#                 self.send_error(401)
#         except:
#             import traceback
#
#             log(traceback.format_exc())
#             self.send_error(500)
#
#     def delete(self, id):
#         try:
#             dao = CmsArticleDao()
#             if dao.validptn(self.get_secure_cookie('username'), id) or (self.get_secure_cookie('role') == 'admin'):
#                 dao.remove_article(id)
#                 self.set_header('Content-Type', 'text/xml; charset=utf-8')
#                 self.write('<article id="' + id + '"/>')
#             else:
#                 self.send_error(401)
#         except:
#             import traceback
#             log(traceback.format_exc())
#             self.send_error(500)
#
# class FindArticleHandler(tornado.web.RequestHandler):
#     __metaclass__ = meta.HandlerMetaClass
#     route = r'/mod/cms/article/(.*)'
#     def get(self, mpid):
#         dao = CmsArticleDao()
#         root = ET.Element('articles')  # 设置根节点
#         for res in dao.find_article(mpid):
#             id, title, priority, summary, thumb, tag_xml = res
#             mess = ET.SubElement(root, 'article', {'id':str(id)})
#             self.__append_element(mess, 'title', title)
#             self.__append_element(mess, 'priority', str(priority))
#             self.__append_element(mess, 'summary', summary)
#             self.__append_element(mess, 'thumb', thumb)
#             if tag_xml is not None:
#                     tag_elm = ET.fromstring(tag_xml.encode('utf-8'))
#                     mess.append(tag_elm)
#         self.set_header('Content-Type', 'text/xml; charset=utf-8')
#         self.write(ET.tostring(root, encoding='UTF-8'))
#
#     def __append_element(self, parent, tag, value):
#         e = ET.Element(tag)
#         if value:
#             e.text = value
#         parent.append(e)
#
# class ArticleListBaseHandler(tornado.web.RequestHandler):
#     def initialize(self):
#         self.dao = CmsArticleDao()
#
#     def get_by_mpid(self, mpid):
#         #self.write(' and '.join(self.get_arguments('tag')))
#         try:
#             dao = self.dao
#             root = ET.Element('articles')   # 设置根节点
#             taglist = self.get_arguments('tag') or []    # 拿到get方法上URL传过来的标签
#             for result in dao.query_tag(mpid, taglist):
#                 id, mpid, priority, title, content, summary, thumb, images_xml, tag_xml = result
#                 mess = ET.SubElement(root, 'article', {'site-id': str(mpid), 'id': str(id)})  # 设置子节点 属性值
#                 self.__append_element(mess, 'priority', str(priority))  # 设置孙节点
#                 self.__append_element(mess, 'title', title)
#                 self.__append_element(mess, 'content', content)
#                 self.__append_element(mess, 'summary', summary)
#                 self.__append_element(mess, 'thumb', thumb)
#                 if images_xml is not None:
#                     img_elm = ET.fromstring(images_xml.encode('utf-8'))
#                     mess.append(img_elm)
#                 if tag_xml is not None:
#                     tag_elm = ET.fromstring(tag_xml.encode('utf-8'))
#                     mess.append(tag_elm)
#             self.set_header('Content-Type', 'text/xml; charset=utf-8')
#             self.write(ET.tostring(root, encoding='UTF-8'))
#         except:
#             import traceback
#             err = traceback.format_exc()
#             log(err)
#             self.send_error(500)
#             self.write(err)
#
#     def __append_element(self, parent, tag, value):
#         e = ET.Element(tag)
#         if value:
#             e.text = value
#         parent.append(e)
#
#
# class QueryCmsArticleListHandler(ArticleListBaseHandler):
#     __metaclass__ = meta.HandlerMetaClass
#     route = r'/mparticlelist/(.*)'
#
#     def get(self, mpid_str):
#         self.get_by_mpid(int(mpid_str))
#
#
#
# class QueryCmsArticleModHandler(ArticleListBaseHandler):
#     __metaclass__ = meta.HandlerMetaClass
#     route = r'/mod/cms/article'
#
#     def get(self):
#          dao = self.dao
#          ghid = self.get_secure_cookie('ghid')
#          if ghid:
#             self.get_by_mpid(dao.query_mpid(ghid))
#          else:
#              self.send_error(401)
#
#
# class CmsArticleDao(object):
#     def __init__(self):
#         self.db = Mysqldb()
#         self.__create_table(self.db)
#
#     def __create_table(self, db):
#         db.execute('''
#             CREATE TABLE IF NOT EXISTS  weicbd_mp_article (
#             id bigint NOT NULL AUTO_INCREMENT,
#             priority  bigint not null,
#             title varchar(100) not null,
#             content varchar(500) null,
#             tag varchar(999) null,
#             summary varchar(50) null,
#             thumb varchar(255) null,
#             images text null,
#             mpid bigint null,
#             FOREIGN KEY (mpid) REFERENCES weicbd_mp_site(id),
#             PRIMARY KEY (id)
#             )''')
#         db.commit()
#
#     def query_article(self):
#         return self.db.fetchall('select id,title,content,tag,mpid from weicbd_mp_article')
#     # 检索明细
#     def query_tag(self, mpid, taglist):
#         if taglist:
#             substring = ' and '.join(['(count(/tags/tag[contains(., "/%s/")]) >=1)' % x for x in taglist])
#             sql = 'SELECT id, mpid, priority, title, content, summary, thumb, images, tag from weicbd_mp_article where id in (select ft.id from (SELECT id, EXTRACTVALUE( tag,\'%s\' ) as flag FROM weicbd_mp_article) as ft where ft.flag=1) and mpid=%d' % (substring, mpid)
#             return self.db.fetchall(sql)
#         else:
#             return self.db.fetchall( 'SELECT id, mpid, priority, title, content, summary, thumb, images, tag from weicbd_mp_article where mpid=%s', (mpid, ))
#
#     def query_mpid(self, ghid):
#         n, =  self.db.fetchone('select id from weicbd_mp_site where ghid=%s', (ghid,)) or (None, )
#         return n
#
#     # 概要搜索
#     def find_article(self, mpid):
#         return self.db.fetchall('select id, title, priority, summary, thumb, tag from weicbd_mp_article  where mpid=%s',(mpid,)) or []
#
#
#     def create_article(self, mpid, priority, title, content, summary, thumb, images, tag):
#         article = self.db.execute( 'insert into weicbd_mp_article (priority, title, content, tag, summary, thumb, images, mpid)  values(%s, %s, %s, %s, %s,%s ,%s,%s)',(priority, title, content, tag, summary, thumb, images, mpid))
#         self.db.commit()
#         return article
#
#     def update_article(self, priority, title, content, tag, summary, thumb,images, id):
#         fessay, = self.db.fetchone('select title from weicbd_mp_article where id=%s', (id,))
#         if fessay is not None:
#             article = self.db.execute('update weicbd_mp_article  set priority  = %s, title = %s, content = %s, summary=%s, thumb=%s, images=%s,tag = %s where id = %s',(priority, title, content, summary, thumb, images, tag, id))
#             self.db.commit()
#             return article
#
#     def remove_article(self, id):
#         self.db.execute('delete from weicbd_mp_article where id=%s', (id,))
#         self.db.commit()
#
#     def validmp(self, username, mpid):
#         n, = self.db.fetchone('SELECT COUNT(a.ID) FROM weicbd_account a, weicbd_mp_site m WHERE m.user_id=a.id AND a.username=%s AND m.id=%s',(username, mpid))
#         return n == 1
#
#     def validptn(self, username, id):
#         n, = self.db.fetchone('SELECT COUNT(a.ID) FROM weicbd_account a, weicbd_mp_site m, weicbd_mp_article p WHERE p.mpid=m.id AND m.user_id=a.id AND a.username=%s AND p.id=%s',(username, id))
#         return n == 1
#
