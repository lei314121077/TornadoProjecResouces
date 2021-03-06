#! /usr/bin/env python
# -*- coding: utf-8 -*-

from orm import Base
from sqlalchemy import String, Column, ForeignKey, Integer, Integer, DateTime, Boolean, Table, Text
from sqlalchemy.orm import relationship, backref

__author__ = 'chinfeng'

article_tag_rel = Table('weicbd_article_tag_rel', Base.metadata,
    Column('article_id', Integer, ForeignKey('weicbd_mp_cms_article.id')),
    Column('tag_id', Integer, ForeignKey('weicbd_mp_tag.id'))
)


class Article(Base):
    __tablename__ = 'weicbd_mp_cms_article'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    dt = Column(DateTime)
    content = Column(Text)
    summary = Column(String(500))
    priority = Column(Integer)
    thumb = Column(String(500))
    images = Column(Text)
    enabled = Column(Boolean)
    mpid = Column(Integer, ForeignKey('weicbd_mp_site.id'))
    tag_id = Column(Integer, ForeignKey('weicbd_mp_tag.id'))

    mpsite = relationship('MpSite', backref=backref('articles'))
    tags = relationship('Tag', secondary=article_tag_rel, backref='articles')

    def __init__(self, title, dt, summary, content, priority=0, thumb=None, images='<images/>', enabled=True):
        self.title = title
        self.dt = dt
        self.summary = summary
        self.content = content
        self.priority = priority
        self.thumb = thumb
        self.images = images
        self.enabled = enabled
