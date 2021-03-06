#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = '北极鱼'

from orm import Base
from sqlalchemy.schema import Table
from sqlalchemy import String, Column, ForeignKey, Integer, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from uuid import uuid4
from datetime import datetime

class  FlowerUser(Base):# 用户
    __tablename__ = 'flower_user_table'

    user_id = Column(Integer, primary_key=True, autoincrement=True)  # 用户编号
    user_name = Column(String(200))   # 用户名称
    user_email = Column(String(200))   # 用户邮箱
    user_mobile = Column(String(200))   # 用户手机
    user_password = Column(String(200))  # 用户密码

    user_typeid = Column(Integer, ForeignKey('flower_usertype_table.utype_id'))
    usertype = relationship('FlowerUserType', backref=backref('flowerusertype, uselist=False'))

    def __init__(self, user_name, user_typeid, user_email, user_mobile, user_password):
        self.user_name = user_name
        self.user_typeid = user_typeid
        self.user_email = user_email
        self.user_mobile = user_mobile
        self.user_password = user_password


class FlowerUserType(Base):# 用户类型
    __tablename__ = 'flower_usertype_table'

    utype_id = Column(Integer, primary_key=True, autoincrement=True)  # 用户类型编号
    utype_name = Column(String(200))  # 用户类型名称

    #FlowerUser = relationship("FlowerUser")
    #user = relationship('FlowerUser', backref=backref('flower_user_table, uselist=False'))

    def __init__(self, utype_name):
        self.utype_name = utype_name