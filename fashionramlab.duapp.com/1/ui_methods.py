#! /usr/bin/env python
# -*- coding: utf-8 -*-

from model.module import ModuleDeployment
from orm import getSession


def fun(handler, id):
    p = clsname.split('.')
    c = __import__(module[:-3], locals(), globals())
    return 'Shit! %s, %s' % (cls, id)


def get_arguments_dict(handler):
    args = { k: v[0] if len(v) == 1 else v for k, v in handler.request.arguments.items() }
    if 'weicbd_wrapper_page' in args:
        del args['weicbd_wrapper_page']
    return args


def get_module_template(handler, id):
    session = getSession()
    md = session.query(ModuleDeployment).filter(ModuleDeployment.id == id).first()
    if md:        
        clsname = md.cls
        ps = clsname.split('.')
        cls = __import__('.'.join(ps[:-1]), globals(), locals(), fromlist=(ps[-1], ))        
        return cls.__dict__[ps[-1]].__module_template__

    