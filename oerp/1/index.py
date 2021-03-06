#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.wsgi
import os
import meta
import traceback
import sys
import openpy.article, openpy.updoad


class MainHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/handlers'
    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<handlers>')
        for u in self.application.handlers[0][1]:
            self.write('<handle><route>%s</route><class>%s</class></handle>' % (u.regex.pattern, u.handler_class.__name__))
        self.write('</handlers>')
 

class LogHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/log'
    def get(self):
        self.write('<html><body>')
        from db import get_log_list
        self.write('<hr/>'.join(['<p>%s</p>' % l.content for l in get_log_list()]))
        self.write('</body></html>')

class PluginListHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/replyplugin'
    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<plugins>')
        for k, v in meta.PluginMetaClass.plugins.items():
            self.write('<plugin><name>%s</name><class>%s</class></plugin>' % (v.name, k))
        self.write('</plugins>')


class ModuleListHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/modules'
    def get(self):
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<modules>')
        for k, v in meta.ModuleMetaClass.modules.items():
            self.write('<module><name>%s</name><version>%s</version><class>%s</class><page>/wrapper/%s</page></module>' % (v.__module_name__, v.__module_version__, k, v.__module_template__))
        self.write('</modules>')


class CrossDomainHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/cross'

    def post(self):
        from db import log
        import xml.etree.ElementTree as ET
        import urllib2
        try:

            root = ET.fromstring(self.request.body)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            request = urllib2.Request(root.find('url').text)
            if root.find('method').text.upper() == 'GET':
                response = opener.open(request)
            elif root.find('method').text.upper() == 'POST':
                response = opener.open(request, root.find('data').text.encode('utf-8'))

            self.write(response.read())
        except:
            import traceback
            log(traceback.format_exc())
            self.write_error(500)


class ImportCheckHandler(tornado.web.RequestHandler):
    __metaclass__ = meta.HandlerMetaClass
    route = r'/importcheck'

    def get(self):
        import sys
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(u'<modules>')
        map(lambda module: self.write(u'<module>%s</module>' % module), sys.modules)
        self.write(u'</modules>')
        
        
class TemplateHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.add_header('Cache-control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.add_header('Expires', '0')

    def get(self, path):
        args = { k: v[0] if len(v) == 1 else v for k, v in self.request.arguments.items() }
        self.render(path, **args)

# class MyStaticFileHandler(tornado.web.StaticFileHandler):
#     def set_extra_headers(self, path):
#         self.add_header('Cache-control', 'no-store, no-cache, must-revalidate, max-age=0')
#         self.add_header('Expires', '0')

        
class PortalWrapperHandler(meta.RequestHandlerBase):
    __route__ = r'/portal/(.*)'
    
    def prepare(self):
        self.add_header('Cache-control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.add_header('Expires', '0')
        
    def get(self, path):
        args = { k: v[0] if len(v) == 1 else v for k, v in self.request.arguments.items() }
        args['weicbd_wrapper_page'] = (r'portal/%s' % path)
        self.render('wrapper.html', **args)
        
class PortalWrapperHandler(meta.RequestHandlerBase):
    __route__ = r'/dialog/(.*)'
    
    def prepare(self):
        self.add_header('Cache-control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.add_header('Expires', '0')
        
    def get(self, path):
        args = { k: v[0] if len(v) == 1 else v for k, v in self.request.arguments.items() }
        args['weicbd_wrapper_page'] = (r'dialog/%s' % path)
        self.render('dialog.html', **args)

class TestWrapperHandler(meta.RequestHandlerBase):
    __route__ = r'/w/(.*)'
    
    def prepare(self):
        self.add_header('Cache-control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.add_header('Expires', '0')
        
    def get(self, path):
        args = { k: v[0] if len(v) == 1 else v for k, v in self.request.arguments.items() }
        args['weicbd_wrapper_page'] = (r'w/%s' % path)
        self.render('w.html', **args)


class MainHandler(meta.RequestHandlerBase):
    __route__ = r'/'
    def get(self):
        self.redirect('/index.htm')        
app_root = os.path.dirname(__file__)
settings = { 
    'static_path': os.path.join(app_root, 'static'),
    'template_path': os.path.join(app_root, 'templates'),
    'gzip': True,
    'debug': True,
    'cookie_secret': 'X9Plz67NkE63PbF1rkY5rc36LcfqCta1',
    'login_url': '/login.html',
#    'ui_methods': ui_methods,
 }

handlers = meta.HandlerMetaClass.handlers + [
    (r'/(portal/.*)', TemplateHandler),
    #(r'/(.*\.html)', TemplateHandler),
	(r'/(.*\.html)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
	(r'/(.*\.htm)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    # (r'/(.*\.htm)', MyStaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.css)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.map)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.js)',  tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.png)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.jpg)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.xml)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.xsl)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
    (r'/(.*\.svg)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
]
app = tornado.wsgi.WSGIApplication(handlers, **settings)

from sys import modules
if 'bae' in modules:
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
elif 'sae' in modules:
    import sae
    application = sae.create_wsgi_app(app)
else:
    application = app
