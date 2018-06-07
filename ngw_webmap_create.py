# -*- coding: utf-8 -*-

'''

'''

#создаёт в группе ресурсов wfs-сервис со всеми слоями
from __future__ import unicode_literals
import os
import json

#для создания ключей транслитом
from transliterate import translit, get_available_language_codes
import re

from operator import itemgetter

import argparse
def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 45

    parser = argparse.ArgumentParser(description='''Script walks through group in NextGIS Web
Creating WMS-service with all vector and rasters styles from this group.

Скрипт проходит по заданной группе в инстансе NextGIS Web
Записывает все стили
Создаёт WMS-сервис со всеми стилями из этой группы.''',
            formatter_class=PrettyFormatter)
    parser.add_argument('--url', type=str,required=True, help='NGW instance url')
    parser.add_argument('--login', default='administrator', required=False, help = 'ngw login')
    parser.add_argument('--password', default='admin', required=False, help = 'ngw password')
    parser.add_argument('--parent', type=int, help='id of parent group', default=0, required=False)
    sorting_group_parser = parser.add_mutually_exclusive_group(required=False)
    sorting_group_parser.add_argument('--reverse', dest='reverse', help = 'Reverse sort', action='store_true',default=False)
    sorting_group_parser.add_argument('--straight', dest='reverse', help = 'straight sort', action='store_false',default=True)
    
    parser.epilog = \
        '''Samples: 

#upload all geojsons and geotiff from current folder
time python %(prog)s --login admin --password pass  --parent 499  --url http://trolleway.nextgis.com

''' \
        % {'prog': parser.prog}
    return parser

URL = 'http://example.com'
AUTH = ('administrator', 'admin')


import requests
from json import dumps
from datetime import datetime

parser = argparser_prepare()
args = parser.parse_args()

URL = args.url
AUTH = (args.login, args.password)
PARENT=args.parent
REVERSE = args.reverse
args = None #don't use afterwards


s = requests.Session()


def req(method, url, json=None, **kwargs):
    """ Простейшая обертка над библиотекой requests c выводом отправляемых
    запросов в stdout. К работе NextGISWeb это имеет малое отношение. """

    jsonuc = None

    if json:
        kwargs['data'] = dumps(json)
        jsonuc = dumps(json, ensure_ascii=False)

    req = requests.Request(method, url, auth=AUTH, **kwargs)
    preq = req.prepare()

    print ""
    print ">>> %s %s" % (method, url)

    if jsonuc:
        print ">>> %s" % jsonuc

    resp = s.send(preq)

    assert resp.status_code / 100 == 2

    jsonresp = resp.json()

    for line in dumps(jsonresp, ensure_ascii=False, indent=4).split("\n"):
        print "<<< %s" % line

    return jsonresp

# Обертки по именам HTTP запросов, по одной на каждый тип запроса

def get(url, **kwargs): return req('GET', url, **kwargs)            # NOQA
def post(url, **kwargs): return req('POST', url, **kwargs)          # NOQA
def put(url, **kwargs): return req('PUT', url, **kwargs)            # NOQA
def delete(url, **kwargs): return req('DELETE', url, **kwargs)      # NOQA

# Собственно работа с REST API

iturl = lambda (id): '%s/api/resource/%d' % (URL, id)
courl = lambda: '%s/api/resource/' % URL
childsurl = lambda (id): '%s/api/resource/?parent=%d' % (URL, id)


# Указываем группу с которой работаем
grpid=PARENT

# Получаем название 

group = get(iturl(grpid))

# Получить все элементы любого уровня вложенности это слишком олимпиадная задача



# Проходим по группе, определяем данные слоёв

childs = get(childsurl(grpid))


# Начинаем добавление WMS-сервиса

# Проходим по группе, запоминаем все ID стилей векторных слоёв. Если у одного слоя несколько стилей - значит так надо, запоминаем все

stylesForService=list() #у одного слоя может быть много стилей
childs = get(childsurl(grpid))
for child in childs:
    data=child
    if data['resource']['cls'] in ('vector_layer','raster_layer'):    
        currentSyles= get(childsurl(child['resource']['id']))
        for style in currentSyles:
            stylesForService.append(style)
            #print currentSyles[0]['resource']['id']

#Конструируем словарь с стилями, который передадим при создании WMS-сервиса
layersForWMS=list()
for style in stylesForService:
    print style['resource']['display_name']
    wmsLayerDef=dict()
    wmsLayerDef['display_name']=style['resource']['display_name']
    wmsLayerDef['keyname']=translit(style['resource']['display_name'],'ru', reversed=True)
    wmsLayerDef['keyname']=re.sub(r'\'+', '', wmsLayerDef['keyname']) #remove symbols
    wmsLayerDef['keyname']=re.sub(r'\s+', '_', wmsLayerDef['keyname']) #remove symbols
    wmsLayerDef['resource_id']=style['resource']['id']
    wmsLayerDef['min_scale_denom']=None
    wmsLayerDef['max_scale_denom']=None
    layersForWMS.append(wmsLayerDef)
	
#Sort
newlist = sorted(layersForWMS, key=lambda k: k['display_name'], reverse = REVERSE) 
layersForWMS = newlist
newlist = None

	
# Создаём WMS-сервис
'''
wmsserv = post(courl(), json=dict(
    resource=dict(cls='wmsserver_service', parent=dict(id=grpid), display_name=group['resource']['display_name']+' WMS-сервис'),
    wmsserver_service=dict()))   
'''


#Конструируем словарь с стилями, который передадим при создании вебкарты
layersForWebmap=list()
for style in stylesForService:
    print style['resource']['display_name']
    webmapLayerDef=dict()
    webmapLayerDef['display_name']=style['resource']['display_name']
    webmapLayerDef['layer_adapter']='tile'
    webmapLayerDef['layer_enabled']=False
    #webmapLayerDef['draw_order_position']=None
    #webmapLayerDef['layer_max_scale_denom']=None
    webmapLayerDef['item_type']='layer'
    webmapLayerDef['layer_style_id']=style['resource']['id']

    layersForWebmap.append(webmapLayerDef)

#Sort
newlist = sorted(layersForWebmap, key=lambda k: k['display_name'], reverse = REVERSE) 
layersForWebmap = newlist
newlist = None

#содержимое папки
RootElements=list()
element = dict(
        item_type='group',group_expanded=True,display_name=group['resource']['display_name'],
        children=layersForWebmap
    )
RootElements.append(element)

# В children должен быть список из словарей
webmap = post(courl(), json=dict(
    resource=dict(cls='webmap', parent=dict(id=grpid), display_name=group['resource']['display_name']+' Вебкарта'),
    webmap=dict(
        root_item=dict(
	item_type='root',
    children=RootElements ) )))     
    

quit() 
