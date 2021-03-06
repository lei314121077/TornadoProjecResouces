import tornado.web, meta, auth, weicbd.aaa
import xml.etree.ElementTree as ET
from db import Mysqldb

class UploadFileHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/upload'
    def post(self):
        file_metas = self.request.files['file']
        username = self.get_secure_cookie('username')
        aaadao = weicbd.aaa.AAADao()
        account_id=aaadao.get_user(username)[0]
        for meta in file_metas:
            filename = meta['filename']
            imagebinary = meta['body']

            route = r'/uploadimg/'+str(account_id)+'/'+filename+''
            self.save_to_bcs(route,imagebinary)
            self.write('<image src="%s"/>' % route)
            #self.addImage(filename,imagebinary,username)


    def addImage(self,filename,imagebinary,username):
        dao = UploadDao()
        account_id, = self.db.fetchone('select id from weicbd_account where username=%s',(username,)) or (None, )
        dao.create_images(filename,imagebinary,account_id)


    def save_to_bcs(self, path, body):
        from bae.core import const
        from bae.api import bcs
        import base64
        baebcs = bcs.BaeBCS(const.BCS_ADDR, const.ACCESS_KEY, const.SECRET_KEY)
        baebcs.put_object(u'fashionramlab', path, base64.b64encode(body))


class GetUpload(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/uploadimg/(.*)'
    def get(self, sub_path):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        from bae.core import const
        from bae.api import bcs
        import base64
        baebcs = bcs.BaeBCS(const.BCS_ADDR, const.ACCESS_KEY, const.SECRET_KEY)
        e, response = baebcs.get_object(u'fashionramlab', r'/uploadimg/' + sub_path)
        self.write(base64.b64decode(response))


class FindListGetUpload(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/myimg'
    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        from bae.core import const
        from bae.api import bcs

        username = self.get_secure_cookie('username')
        if username is not None:
            account_id=weicbd.aaa.AAADao().get_user(username)[0]
            import base64
            baebcs = bcs.BaeBCS(const.BCS_ADDR, const.ACCESS_KEY, const.SECRET_KEY)
            e, response = baebcs.list_objects(u'fashionramlab', r'/uploadimg/' + str(account_id))
            self.write('<images>')
            for result in response:
                self.write('<image>%s</image>' % result)
            self.write('</images>')
        else:
            self.write('<images/>')




#
# class GetUploadFileHandler(tornado.web.RequestHandler):
#     __metaclass__ = meta.HandlerMetaClass
#     route = r'/myimg/(.*)'
#     def get(self,mg):
#         dao= UploadDao()
#         root = ET.Element('images')
#         for result in dao.all_images(mg):
#             id, filename = result
#             img = ET.SubElement(root, 'image', id=str(id))
#             self.__append_element(img, 'filename', filename)
#         self.set_header('Content-Type', 'text/xml; charset=utf-8')
#         self.write(ET.tostring(root, encoding='UTF-8'))
#
#     def __append_element(self, parent, tag, value):
#          e = ET.Element(tag)
#          if value:
#              e.text = value
#          parent.append(e)







class UploadDao(object):
    def __init__(self):
        self.db =Mysqldb()
        self.__create_table(self.db)

    def __create_table(self, db):
        db.execute('''
            CREATE TABLE IF NOT EXISTS weicbd_account_image (
                id bigint NOT NULL AUTO_INCREMENT,
                filename varchar(255) NOT NULL,
                imagebinary binary(225) NOT NULL,
                account_id bigint NOT NULL,
                FOREIGN KEY (account_id) REFERENCES weicbd_account(id),
                PRIMARY KEY (id)
            ) DEFAULT CHARACTER SET=utf8;
        ''')

    def create_images(self, filename,imagebinary,account_id):
            images = self.db.execute('insert into weicbd_account_image(filename,imagebinary,account_id) values(%s,%s,%s)',(filename,imagebinary,account_id))
            self.db.commit()
            return images

    def all_images(self,mg):
        return self.db.fetchall('select id,filename from weicbd_account_image where account_id= %s ',(mg,))

    def find_images(self,id):
        return self.db.fetchone('select imagebinary from weicbd_account_image where id=%s',(id,))