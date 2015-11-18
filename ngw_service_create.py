# -*- coding: utf-8 -*-


#создаёт в группе ресурсов wfs-сервис со всеми слоями
from __future__ import unicode_literals
import os
import json

#для создания ключей транслитом
from transliterate import translit, get_available_language_codes
import re

#для создания стилей рандомного цвета
import random


URL = 'http://example.com'
AUTH = ('administrator', 'admin')


import requests
from json import dumps
from datetime import datetime



def generateMapstyle(geometryType):
    #Возвращает простой картостиль. При каждом вызове генерирует случайный цвет
    defaultMapstyles=dict()
    defaultMapstyles['LINESTRING']='''
    <map>
    <layer>
    <class>
    <style>
    <color red=\"'''+str(random.randint(50, 180))+'''\" green=\"'''+str(random.randint(50, 180))+'''\" blue=\"'''+str(random.randint(50, 180))+'''\"/>
    <width>5</width>
    </style>
    </class>
    </layer>
    </map>
    '''
    defaultMapstyles['POLYGON']='''
    <map>
    <layer>
    <class>
    <style>
    <color red=\"'''+str(random.randint(50, 180))+'''\" green=\"'''+str(random.randint(50, 180))+'''\" blue=\"'''+str(random.randint(50, 180))+'''\"/>
    <outlinecolor red=\"'''+str(random.randint(50, 180))+'''\" green=\"'''+str(random.randint(50, 180))+'''\" blue=\"'''+str(random.randint(50, 180))+'''\"/>
    </style>
    </class>
    </layer>
    </map>
    '''
    defaultMapstyles['POINT']='''
    <map>
    <symbol>
    <type>ellipse</type>
    <name>circle</name>
    <points>1 1</points>
    <filled>true</filled>
    </symbol>
    <layer>
    <class>
    <style>
    <color red=\"'''+str(random.randint(50, 180))+'''\" green=\"'''+str(random.randint(50, 180))+'''\" blue=\"'''+str(random.randint(50, 180))+'''\"/>
    <outlinecolor red=\"'''+str(random.randint(50, 180))+'''\" green=\"'''+str(random.randint(50, 180))+'''\" blue=\"'''+str(random.randint(50, 180))+'''\"/>
    <symbol>circle</symbol>
    <size>6</size>
    </style>
    </class>
    </layer>
    </map>
    '''
    return defaultMapstyles[geometryType]





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
grpid=89

# Получаем название 

group = get(iturl(grpid))



# Проходим по группе, определяем данные слоёв

childs = get(childsurl(grpid))
for child in childs:
    data=child
    if data['resource']['cls'] == 'vector_layer':
        layerID=data['resource']['id']
        print str(layerID) +" "+ data['resource']['display_name']+" "+ data['vector_layer']['geometry_type']


        #Проверяем, есть ли у этого векторного слоя какие-нибудь стили
        layerHasVectorStyles=False

        currentSyles= get(childsurl(layerID))
        if len(currentSyles)>0:
            layerHasVectorStyles=True

        # Если у векторного слоя нет ни одного стиля, то добавляем стиль по умолчанию
        if layerHasVectorStyles==True:
            print "Layer " + str(layerID) +" "+ data['resource']['display_name'] + " has vector styles"
        else:
            print "Add vector style to Layer " + str(layerID) +" "+ data['resource']['display_name']

            vectstyle = post(courl(), json=dict(
                resource=dict(cls='mapserver_style', parent=dict(id=layerID), display_name=data['resource']['display_name']),
                mapserver_style=dict(xml=generateMapstyle(data['vector_layer']['geometry_type']))
            ))






# Начинаем добавление WMS-сервиса

# Проходим по группе, запоминаем все ID стилей векторных слоёв. Если у одного слоя несколько стилей - значит так надо, запоминаем все

stylesForService=list() #у одного слоя может быть много стилей
childs = get(childsurl(grpid))
for child in childs:
    data=child
    if data['resource']['cls'] == 'vector_layer':    
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
# Создаём WMS-сервис

wmsserv = post(courl(), json=dict(
    resource=dict(cls='wmsserver_service', parent=dict(id=grpid), display_name=group['resource']['display_name']+' WMS-сервис'),
    wmsserver_service=dict(layers=layersForWMS)))     


# Начинаем добавление WFS-сервиса

# Проходим по группе, запоминаем все ID самих векторных слоёв.

layersForService=list() 
childs = get(childsurl(grpid))
for child in childs:
    layer=child
    if layer['resource']['cls'] == 'vector_layer':    
        wfsLayerDef=dict()
        wfsLayerDef['display_name']=layer['resource']['display_name']
        wfsLayerDef['maxfeatures']=1000
        wfsLayerDef['keyname']=translit(layer['resource']['display_name'],'ru', reversed=True)
        wfsLayerDef['keyname']=re.sub(r'\'+', '', wfsLayerDef['keyname']) #remove symbols
        wfsLayerDef['keyname']=re.sub(r'/+', '_', wfsLayerDef['keyname']) #remove symbols
        wfsLayerDef['keyname']=re.sub(r'\s+', '_', wfsLayerDef['keyname']) #remove symbols
        wfsLayerDef['resource_id']=layer['resource']['id']
        layersForService.append(wfsLayerDef)


# Создаём WFS-сервис

wfsserv = post(courl(), json=dict(
    resource=dict(cls='wfsserver_service', parent=dict(id=grpid), display_name=group['resource']['display_name']+' WFS-сервис'),
    wfsserver_service=dict(layers=layersForService)))     




quit() 