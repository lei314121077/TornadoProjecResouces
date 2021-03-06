#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '北极鱼'

import tornado.web, meta
from sys import modules
import xml.etree.ElementTree as ET
from orm import getSession
from model.upload import Images

class UploadFileHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/upload'
    # 上传文件
    def post(self):
        file_metas = self.request.files['file']
        for meta in file_metas:
            imagebinary = meta['body'] #  图片二进制
            filename = meta['filename']
            self.save_file(filename, imagebinary)

    def save_file(self, filename, imagebinary):
         if 'sae' in modules:
                from sae.storage import Bucket
                fpath = r'http://oerp-oerp.stor.sinaapp.com/'+filename  # 完整的路径
                session = getSession()
                img = Images(filename, fpath)
                session.add(img)
                session.commit()
                bucket = Bucket('oerp')                   # 从云平台拿到一个Bucket容器
                bucket.put_object(filename, imagebinary)   # 存取一个文件到SAE 云平台   bucket.put_object(path,imagebinary)
                self.set_header('Content-Type', 'text/xml; charset=utf-8')
                self.write('<image src="%s"/>' % fpath)
         else:
                import io        # 引入IO包
                with io.open('e:\upload\/'+filename, 'wb') as file:
                    file.write(imagebinary)

class GetUpload(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/uploadimg/(.*)'
    # 下载某个文件
    def get(self, sub_path):
        from sae.storage import Bucket
        bucket = Bucket('oerp')                                  # 从云平台拿到一个Bucket容器
        #imagebinary = meta['body']
        response = bucket.get_object_contents(sub_path, chunk_size=10)    # 取文件    bucket.get_object_contents(u'oerp', r'/uploadimg/' + sub_path)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(response.next())


class FindListGetUpload(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/myimg'
    # 列出云平台的所有文件
    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        if 'sae' in modules:
            from sae.storage import Bucket
            bucket = Bucket('oerp')
            # response = bucket.list(u'oerp', r'/uploadimg/')
            self.write('<images>')
            for result in bucket.list(path=''):         # 从新浪云端拿到所有文件并输出其路径
                self.write('<image>http://oerp-oerp.stor.sinaapp.com/%s</image>' % result.name)
            self.write('</images>')
        else:
            import os
            self.write('<images>')
            path = os.path.normcase("e:/upload/")      #OS.path.normcase方法可一自动把正斜杠转化成反斜杠
            for img in os.listdir('e:\upload'):
                 imagepath = path+img
                 self.write('<image>%s</image>' % imagepath)
            self.write('</images>')


class GetUploadFileHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/openerp/myimg/(.*)'

    def get(self, mg):
        session = getSession()
        root = ET.Element('images')
        img = session.query(Images).filter(Images.filepath == mg).all()
        if img:
            for result in img:
                imgel = ET.SubElement(root, 'image')
                imgel.attrib['id'] = str(result.id)
                ET.SubElement(imgel, 'filename').text = result.filename
                ET.SubElement(imgel, 'filepath').text = result.filepath
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))


