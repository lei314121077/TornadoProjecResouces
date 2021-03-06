﻿#! /usr/bin/env python
# -*- coding: utf-8 -*-

from time import mktime, localtime
import xml.etree.ElementTree as ET
import meta, base64, zlib
from urllib import quote_plus
from db import log
from model.location import MpLocation
from model.mpsite import MpSite

textTmpl = '''
<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%d</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
</xml>
'''


def redirect_url(prefix, url, openid, ghid):
    if url[0:1] == '/':
        from wx import encode_s_parameters
        return '%s/mpctx?redirect=%s&s=%s' % (prefix,
                                               quote_plus('%s%sref=weixin.qq.com' % (url, ('?' if '?' not in url else '&'))),
                                               quote_plus(encode_s_parameters(('openid=%s&ghid=%s' % (openid, ghid))))
        )
    else:
        return url


def text_reply(prefix, openid, ghid, content):
    import re
    for url in re.findall(r'<a href="([^"]*)">', content):
        content = content.replace('<a href="%s">' % url, '<a href="%s">' % redirect_url(prefix, url, openid, ghid))
    return textTmpl % (
        openid, ghid, int(mktime(localtime())), content)


def articles_reply(prefix, openid, ghid, articles):
    root = ET.Element('xml')
    __append_element(root, 'ToUserName', openid)
    __append_element(root, 'FromUserName', ghid)
    __append_element(root, 'CreateTime', str(int(mktime(localtime()))))
    __append_element(root, 'MsgType', 'news')
    __append_element(root, 'ArticleCount', str(len(articles)))
    arts_elm = ET.SubElement(root, 'Articles')
    for article in articles:
        url = article['Url']
        if 'ext' in article:
            for k, v in article['ext'].items():
                if v == 'openid':
                    url = ('%s%s%s=%s' % (url, ('?' if '?' not in url else '&'), k, openid))
                if v == 'ghid':
                    url = ('%s%s%s=%s' % (url, ('?' if '?' not in url else '&'), k, ghid))

        item = ET.SubElement(arts_elm, 'item')
        __append_element(item, 'Title', article['Title'])
        __append_element(item, 'Description', article['Description'])
        __append_element(item, 'PicUrl', article['PicUrl'])
        __append_element(item, 'Url', redirect_url(prefix, url, openid,
                                                   ghid))
    rep_xml = ET.tostring(root, encoding='UTF-8')
    return rep_xml


def __append_element(parent, tag, value):
    e = ET.Element(tag)
    if value is not None:
        e.text = value
    parent.append(e)

class BasePlugin(object):
    def response_message(self, request=None):
        pass


class TestingReplyPlugin(BasePlugin):
    __metaclass__ = meta.PluginMetaClass
    name = '“测试中”的文本回复'

    def response_message(self, request):
        return textTmpl % (
        self.parameters['FromUserName'], self.parameters['ToUserName'], int(mktime(localtime())), '内容测试中，敬请期待')


class TextLinkPlugin(BasePlugin):
    __metaclass__ = meta.PluginMetaClass
    name = '文本插件'

    def response_message(self, request):
        content = self.settings['Content']
        prefix = '%s://%s' % (request.protocol, request.host)
        return text_reply(prefix, self.parameters['FromUserName'], self.parameters['ToUserName'], content)


class ArticlePlugin(BasePlugin):
    __metaclass__ = meta.PluginMetaClass
    name = '图文插件'

    def response_message(self, request):
        prefix = '%s://%s' % (request.protocol, request.host)
        return articles_reply(prefix, self.parameters['FromUserName'], self.parameters['ToUserName'], self.settings['Articles'])


class MenuPlugin(BasePlugin):
    __metaclass__ = meta.PluginMetaClass
    name = '菜单插件'

    def response_message(self, request):
        reply = self.settings.get(self.parameters['EventKey'], None)
        if reply is not None:
            prefix = '%s://%s' % (request.protocol, request.host)

            if 'Content' in reply:
                return text_reply(prefix, self.parameters['FromUserName'], self.parameters['ToUserName'], reply['Content'])
            if 'Articles' in reply:
                return articles_reply(prefix, self.parameters['FromUserName'], self.parameters['ToUserName'], reply['Articles'])


class LocationPlugin(BasePlugin):
    __metaclass__ = meta.PluginMetaClass
    name = '地理位置插件'

    def response_message(self, request):
        lx = self.parameters['Location_X']
        ly = self.parameters['Location_Y']
        route_page = self.settings['route-page']
        reply = self.settings

        prefix = '%s://%s' % (request.protocol, request.host)
        if 'Content' in reply:
            return text_reply(prefix, self.parameters['FromUserName'], self.parameters['ToUserName'], '<a href="%s%sx=%s&y=%s">%s</a>'  % (route_page, '?' if '?' not in route_page else '&', ly, lx, reply['Content']))
        if 'Article' in reply:
            reply['Article']['Url'] = '%s%sx=%s&y=%s' % (reply['Article']['Url'],  '?' if '?' not in route_page else '&', ly, lx)
            return articles_reply(prefix, self.parameters['FromUserName'], self.parameters['ToUserName'], (reply['Article'],))


class LocationListPlugin(BasePlugin):
    __metaclass__ = meta.PluginMetaClass
    name = '地理位置列表插件'

    def response_message(self, request):
        from db import log
        from orm import getSession
        ghid = self.parameters['ToUserName']
        openid = self.parameters['FromUserName']
        locs = getSession().query(MpLocation).join(MpSite).filter(MpSite.ghid == ghid).order_by(MpLocation.priority)
        prefix = '%s://%s' % (request.protocol, request.host)
        url = self.settings['url']
        articles = []
        for loc in locs:
            article = {}
            reply_url = '%s%sdlon=%f&dlat=%f&slon=%s&slat=%s' % (url,  '?' if '?' not in url else '&', loc.lon, loc.lat, self.parameters['Location_X'], self.parameters['Location_Y'])
            article['Title'] = loc.name
            article['Description'] = loc.address
            article['PicUrl'] = loc.thumb
            article['Url'] = reply_url
            articles.append(article)
        return log(articles_reply(prefix, openid, ghid, articles))
