#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
We have list of resources groups in NextGIS Web.
Script generate csv with names and id-s of vector layers.

Имеется NGW. В ней лежат группы ресурсов, в группах - слои.
Имеется набор id-шников групп ресурсов.
Нужно получить csv-файл с называнием векторных слоёв и их id.
'''

#делаем штуки для подключения к ngw
from __future__ import unicode_literals
import os
from owslib.wfs import WebFeatureService

URL = 'http://78.46.100.76/opendata_ngw'
AUTH = ('administrator', 'admin')

groups=(109,128)







import requests
from json import dumps
from datetime import datetime



import pprint
pp = pprint.PrettyPrinter(indent=4)



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
childsurl = lambda (id): '%s/resource/%d/child/' % (URL, id)
courl = lambda: '%s/api/resource/' % URL




#Печать шапки csv

fs = open('result.csv','w')
fs.write("name,id\n")
fs.close()



for group_id in groups:

    childs=get(childsurl(group_id))

    for layerdesc in childs:
        #pp.pprint(layerdesc)
        if layerdesc['resource']['cls']=='vector_layer':
            

            #модуль csv не работает с файлами открытыми на дозапись, поэтому генерирую строку csv вручную
            export_string=''
            export_string += '"'+unicode(layerdesc['resource']['display_name'])+'",'
            export_string += '"'+str(layerdesc['resource']['id'])+'"'
            export_string += "\n"


            print export_string

            fs = open('result.csv','a')
            fs.write(export_string.encode("UTF-8"))
            fs.close()













