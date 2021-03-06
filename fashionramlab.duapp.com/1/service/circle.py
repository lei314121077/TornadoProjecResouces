#! /usr/bin/env python
# -*- coding: utf-8 -*-

import meta, auth
from model.aaa import Passport
from model.circle import Circle
from model.module import ModuleDeployment
from orm import getSession
from uuid import uuid4
import xml.etree.ElementTree as ET
from service import ServiceHandlerBase


class CircleListHandler(ServiceHandlerBase):
    __route__ = r'/circles'

    def get(self):        
        pp = self.get_current_user()
        if pp:
            session = getSession()
            p = session.query(Passport).filter(Passport.id == pp.get('id')).first()
            root = ET.Element('circles')
            for circle in p.own_circles + p.joined_circles:
                circle_elm = ET.SubElement(root, 'circle', {'id': str(circle.id), 'owner-id': str(circle.owner_id), 'serial': circle.serial})
                ET.SubElement(circle_elm, 'name').text = circle.name
                ET.SubElement(circle_elm, 'description').text = circle.description
                ET.SubElement(circle_elm, 'create-time').text = str(circle.create_time)
                #self.__append_element(circle_elm, 'name', circle.name)
                #self.__append_element(circle_elm, 'description', circle.description)
                #self.__append_element(circle_elm, 'create-time', str(circle.create_time))
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write(ET.tostring(root, encoding='UTF-8'))
        else:
            self.send_error(401)
            
            
class CircleByIdHandler(ServiceHandlerBase):
    __route__ = r'/circle/(.*)'

    def get(self, cid_str):
        cid = int(cid_str)
        root = ET.Element('circle')
        
        session = getSession()
        c = session.query(Circle).filter(Circle.id == cid).first()
        
        if c:
            root.attrib['id'] = str(c.id)
            root.attrib['owner-id'] = str(c.owner_id)
            ET.SubElement(root, 'name').text = c.name
            ET.SubElement(root, 'description').text = c.description
            members_elm = ET.SubElement(root, 'members')
            for m in c.members:
                p = ET.SubElement(members_elm, 'passport')
                p.attrib['id'] = str(m.id)
            
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))

    @auth.authenticated
    def put(self, cid_str):
        cid = int(cid_str)
        root = ET.fromstring(self.request.body)
        session = getSession()

        c = session.query(Circle).filter(Circle.id == cid).first()
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        if c:
            c.name = root.findtext('name')
            c.description = root.findtext('description')
            session.merge(c)
            session.commit()
            self.write('<circle id="%d"/>' % c.id)
        else:
            self.set_status(500)
            self.write('<error>圈子不存在！</error')

        #self.set_header('Content-Type', 'text/xml; charset=utf-8')
        #self.write('<circle id="%d"/>' % c.id)
        #session.close()
        
            
class CircleHandler(ServiceHandlerBase):
    __route__ = r'/circle'
    
    def prepare(self):
        self.add_header('Cache-control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.add_header('Expires', '0')

    @auth.authenticated
    def post(self):
        root = ET.fromstring(self.request.body)
        session = getSession()
        pp = self.get_current_user()
        c = Circle(
            root.findtext('name'),
            root.findtext('description'),
            pp.get('id')
        )
        session.add(c)
        session.commit()

        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<circle id="%d"/>' % c.id)
        session.close()
        
    def get(self):
        # 从引用路径获得id
        referer = self.request.headers.get('Referer', None)
        
        root = ET.Element('circle')
        if referer:
            from urlparse import urlparse, parse_qs
            cid = int(parse_qs(urlparse(referer).query)['id'][0])            
            session = getSession()
            c = session.query(Circle).filter(Circle.id == cid).first()
                    
            root.attrib['id'] = str(c.id)
            root.attrib['owner-id'] = str(c.owner_id)
            ET.SubElement(root, 'name').text = c.name
            ET.SubElement(root, 'description').text = c.description
            members_elm = ET.SubElement(root, 'members')
            for m in c.members:
                p = ET.SubElement(members_elm, 'passport')
                p.attrib['id'] = str(m.id)
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))
        

class JoinCircleHandler(ServiceHandlerBase):
    __route__ = r'/joincircle'

    @auth.authenticated
    def post(self):
        root = ET.fromstring(self.request.body)
        session = getSession()
        pp = self.get_current_user()
        c = session.query(Circle).filter(Circle.id == int(root.attrib['id'])).first()
        if c:
            p = session.query(Passport).filter(Passport.id == pp['id']).first()
            c.members.append(p)
            session.merge(c)            
            session.commit()
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write('<circle id="%d"/>' % c.id)
        else:
            self.send_error(500)

class DeploymentsHandler(ServiceHandlerBase):
    __route__ = r'/deployments/(.*)'
    
    def get(self, cid_str):
        root = ET.Element('deployments')
        cid = int(cid_str)
        root.attrib['circle-id'] = str(cid)
        session = getSession()
        mds = session.query(ModuleDeployment).filter(ModuleDeployment.circle_id == cid).all()
        if mds:            
            for md in mds:
                d_elm = ET.SubElement(root, 'deployment', {'id': str(md.id), 'serial': md.serial})
                ET.SubElement(d_elm, 'name').text = md.name
                ET.SubElement(d_elm, 'class').text = md.cls
                ET.SubElement(d_elm, 'version').text = md.version
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write(ET.tostring(root, encoding='UTF-8'))
        
        
class DeployHandler(ServiceHandlerBase):
    __route__ = r'/deploy/(.*)'
    
    @auth.authenticated
    def post(self, cid_str):
        # 从引用路径获得id
        cid = int(cid_str)        
        root = ET.fromstring(self.request.body)
        session = getSession()
        cls = root.findtext('class')
        name = root.findtext('name')
        version = root.findtext('version')
        md = ModuleDeployment(cls, name, version, uuid4().hex, cid)
        session.add(md)
        session.commit()
        self.set_header('Content-Type', 'text/xml; charset=utf-8')
        self.write('<deployment id="%d"/>' % md.id)
