# -*- coding: utf-8 -*-
'''
Есть слой в ngw с одинаковыми идентификаторами. В слое есть поле с url изображений.
Скрипт выкачивает их, и загружает аттачами к фиче.

Usage: geojson2ngw.py foldername
'''
from __future__ import unicode_literals
import os

URL = 'http://.nextgis.com'
AUTH = ('', '')
GRPNAME = "Загрузка из python"
LAYER = 239
FIELDNAME = 'Ссылка на последнее фото \"Фасад\"'


import requests
from json import dumps
import json
from datetime import datetime

import csv
import sys
import pprint

from contextlib import closing



# Function block to convert a csv file to a list of dictionaries.  Takes in one variable called "variables_file"

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def csv_dict_list(variables_file):
     
    # Open variable-based csv, iterate over the rows and map values to a list of dictionaries containing key/value pairs. Taken from https://overlaid.net/2016/02/04/convert-a-csv-to-a-dictionary-in-python/
 
    reader = unicode_csv_reader(open(variables_file, 'rb'))
    dict_list = []
    for line in reader:
        dict_list.append(line)
    return dict_list



# Пока удаление ресурсов не работает, добавим дату и время к имени группы
GRPNAME = datetime.now().isoformat() + " " + GRPNAME

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
layerfeaturesurl = lambda (id): '%s/api/resource/%d/feature/' % (URL, id)
editfeatureurl = lambda (id): '%s/api/resource/%d/feature/%d' % (URL, id, feature_id)

#загружаем в память json слоя из веба

#req = requests.get(ngw1_url + '/resource/'  + str(937) + '/feature/', auth=ngw1_creds)

layerdata = get(layerfeaturesurl(LAYER))
for feature in layerdata:
    if ((feature['fields'][FIELDNAME] <> '') and (feature['fields'][FIELDNAME] <> None) and (feature['extensions']['attachment'] == None)):
        print feature['id'], feature['fields'][FIELDNAME]


        new_id = feature['id']          #feature id

        #Get file from internet, optionaly with auth
        try:
            with closing(requests.get(feature['fields'][FIELDNAME], auth=('', ''), stream=True)) as f:

                #upload attachment to nextgisweb
                req = requests.put(URL + '/api/component/file_upload/upload', data=f, auth=AUTH)
                json_data = req.json()
                json_data['name'] = feature['fields'][FIELDNAME].split('/')[-1]  #hacking here!

                attach_data = {}
                attach_data['file_upload'] = json_data

                #add attachment to nextgisweb feature
                req = requests.post(layerfeaturesurl(LAYER) + '/' + str(new_id) + '/attachment/', data=json.dumps(attach_data), auth=AUTH)
        except:
            print 'Skip due to http error: ' + str(feature['id']), feature['fields'][FIELDNAME]

quit()

