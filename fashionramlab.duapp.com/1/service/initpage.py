#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json, traceback
import meta
from . import ServiceHandlerBase
from model.aaa import Passport
from orm import getSession

class InitHandler(ServiceHandlerBase):
    __route__ = r'/init'

    def get(self):
        try:
            pp = Passport('admin', 'admin', 'admin')
            session = getSession()
            session.add(pp)
            session.commit()
            self.set_header(u'Content-Type', u'text/xml; charset=utf-8')
            self.write(u'<init>')
            self.write(u'<passport id="%d">%s</passport>' % (pp.id, pp.email))
            self.write(u'</init>')
            session.close()
        except:
            self.error_msg = traceback.format_exc()
            from db import getLogger
            log = getLogger()
            log.error(self.error_msg)
            self.send_error(500)

    def get_error_html(self, status_code, **kwargs):
        self.write(u'<html><body><xmp>%s</xmp></body></html>' % self.error_msg)

class TestHandler(ServiceHandlerBase):
    __route__ = r'/test'
    
    def get(self):
        self.set_header(u'Content-Type', u'text/plain; charset=utf-8')
        self.write(self.get_current_user())
        