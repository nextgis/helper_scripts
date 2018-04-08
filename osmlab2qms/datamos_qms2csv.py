#!/usr/bin/env python
# -*- coding: utf-8 -*-
#******************************************************************************
#
# datamos_qms2csv.py
# ---------------------------------------------------------
# Generate a table with potential services
# More: http://github.com/nextgis/helper_scripts/osmlab
#
# Usage: 
#      usage: datamos_qms2csv.py [-h] [-u]
#      where:
#           -h              show this help message and exit
# Example:
#      python osmlab_qms2csv.py -u
#
# Copyright (C) 2017-present Maxim Dubinin (maxim.dubinin@nextgis.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

import requests
import argparse
import json
from pprint import pprint
import os
import urlparse
import re
import csv
import countryinfo

parser = argparse.ArgumentParser()
parser.add_argument('-u','--update', action="store_true", help='Update data')
args = parser.parse_args()

def downloadDMS(filename):
    #read file from gitlab
    url='https://gitlab.com/nextgis/data.mos.ru/raw/master/datasets.json'

    r = requests.get(url)
    with open(filename, "wb") as data_file:
        data_file.write(r.content)
    print('Fresh dms_full.json dowloaded')
    with open(filename) as data_file:    
        data = json.load(data_file)

    return data

def downloadQMS(filename):
    #qmslist=import_qms()
    url='https://qms.nextgis.com/api/v1/geoservices/?format=json'
    r = requests.get(url)
    
    with open(filename, "wb") as data_file:
        data_file.write(r.content)

    with open(filename) as data_file:    
        qmslist = json.load(data_file)

    newlist=[]

    for layer in qmslist:

        url='https://qms.nextgis.com/api/v1/geoservices/'+str(layer['id'])+'/?format=json'
        print url
        r = requests.get(url)
        data = json.loads(r.content)
        layer.update(data)

        #print layer
        newlist.append(layer)
        with open('qms_full.json', 'wb') as outfile:
            json.dump(newlist, outfile)

def openjson(filename):
    with open(filename) as data_file:
        data = json.load(data_file)

    return data

def getLayerDomain(url):
    '''
    Convert 
    http://tiles{switch:1,2,3,4}-4001b3692e229e3215c9b7a73e528198.skobblermaps.com/TileService/tiles/2.0/00021210101/0/{zoom}/{x}/{y}.png
    to
    skobblermaps.com
    '''
    stripped_url = re.sub('{.+?}', '', url)

    subdomain=''
    url = urlparse.urlparse(stripped_url)
    try:
        subdomain = url.hostname.split('.')[-2] + '.' + url.hostname.split('.')[-1]
    except:
        subdomain=None
    return subdomain

def prepare_url(url):
    url = url.replace('//a.','//')
    if url.find('http://') == 0: url = url.replace('http://','',1)
    if url.find('https://') == 0: url = url.replace('https://','',1)
    url = url.rstrip('?')
    url = url.upper()

    return url

def find_noimport(service_id):
    noimport = open('noimport.txt').read().splitlines()
    if service_id in noimport: 
        result = True
    else:
        result = False

    return result

def find_qmsGeoJSON(url):
    #   Search in qms for layer
    exist_qms = False
    layer = None
    for qmslayer in qmslist:
        if prepare_url(url) in qmslayer['url'].upper():
                exist_qms = True
                layer = qmslayer

    return layer, exist_qms

def find_changes(qmslayer,layer):
    find_changes = ''

    if len(qmslayer['desc'].split(':')) > 1 and layer['Id'] == qmslayer['desc'].split(':')[1].split(';')[0].strip():
        #this service is synced with datamos
        if 'license_url' in layer.keys() and layer['license_url'] != qmslayer['license_url']:
            find_changes = find_changes + ';' + 'license_url'
        if layer['type'] != qmslayer['type']:
            find_changes = find_changes + ';' + 'type'    
        if 'attribution' in layer.keys():
            if 'text' in layer['attribution'].keys() and layer['attribution']['text'].strip() != qmslayer['copyright_text']:
                find_changes = find_changes + ';' + 'copyright_text'
            if 'url' in layer['attribution'].keys() and layer['attribution']['url'] != qmslayer['copyright_url']:
                find_changes = find_changes + ';' + 'copyright_url'
        if layer['name'] != qmslayer['name']:
            find_changes = find_changes + ';' + 'name'
            
    return find_changes        
    
if __name__ == '__main__':
    
    datamos_location = 'c:/work/data.mos.ru/data/'
    
    if not os.path.exists('dms_full.json') or args.update: downloadDMS('dms_full.json')
    if not os.path.exists('qms_full.json') or args.update: downloadQMS('qms_full.json')

    dmslist=openjson('dms_full.json')
    qmslist=openjson('qms_full.json')
    
    fieldnames = ['id', 'qms_id', 'name', 'type', 'exist_qms', 'changes_sync', 'url','url_qms','license_name','license_url','attribution_text','attribution_url','terms_url','available_projections', 'source', 'description']
    
    with open('list.csv', 'wb') as csvfile:
        listwriter = csv.DictWriter(csvfile, fieldnames, delimiter=';',quotechar='"', quoting=csv.QUOTE_ALL)
        headers = {} 
        for n in fieldnames:
            headers[n] = n
        listwriter.writerow(headers)
    
        for datamos_layer in dmslist:
            row=dict()
            row['id'] = datamos_layer['Id']
            if datamos_layer['ContainsGeodata'] == True and os.path.exists(datamos_location + str(row['id']) + '/' + str(row['id']) + '_ff.geojson'):
                row['type'] = 'geojson'
                row['url'] = 'https://gitlab.com/nextgis/data.mos.ru/raw/master/data/%s/%s_ff.geojson' % (str(row['id']),str(row['id']))
                print row['url']
                row['url_qms'] = row['url']

                #data.mos.ru
                row['description'] = (u'Нормализованные (плоская структура) данные с портала открытых данных г. Москвы. Идентификатор: ' + str(row['id']) + ';' + datamos_layer['SefUrl']).encode('utf-8')
                row['source'] = 'http://data.mos.ru/opendata/' + datamos_layer['SefUrl']

                #Check if services already exists in QMS based on it's url
                exist_qms = ''
                qmslayer,exist_qms = find_qmsGeoJSON(row['url_qms'])
                row['exist_qms'] = exist_qms

                row['id'] = datamos_layer['Id']
                row['name'] = (datamos_layer['Caption'] + u' (Москва)').encode('utf-8')
                
                row['license_name'] = 'Типовые условия использования общедоступной информации, размещаемой в информационно-телекоммуникационной сети "Интернет" в форме открытых данных'
                row['license_url'] = 'http://data.gov.ru/information-usage'
                row['attribution_text'] = 'Портал открытых данных Правительства города Москвы'
                row['attribution_url'] = 'https://data.mos.ru'
                row['terms_url'] = 'https://data.mos.ru/about/terms'
                row['available_projections'] = '[4326]'

                if exist_qms:
                    changes_exist = find_changes(qmslayer,datamos_layer)
                    row['changes_sync'] = changes_exist
                    row['qms_id'] = qmslayer['id']
                else:
                    if find_noimport(row['id']): row['exist_qms'] = 'Skip'

                listwriter.writerow(row)
