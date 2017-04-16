#!/usr/bin/env python
# -*- coding: utf-8 -*-
#******************************************************************************
#
# osmlab_qms2csv.py
# ---------------------------------------------------------
# Send notifications about new QMS services to Telegram channel through a bot
# More: http://github.com/nextgis/helper_scripts/osmlab
#
# Usage: 
#      usage: osmlab_qms2csv.py [-h] [-u]
#      where:
#           -h              show this help message and exit
# Example:
#      python osmlab_qms2csv.py -u
#
# Copyright (C) 2017-present Maxim Dubinin (maxim.dubinin@nextgis.com), Artem Svetlov <artem.svetlov@nextgis.com>
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

def downloadOSMLab(filename):
    #read file from github
    url='https://github.com/osmlab/editor-layer-index/raw/gh-pages/imagery.json'

    r = requests.get(url)
    with open(filename, "wb") as data_file:
        data_file.write(r.content)
    print('Fresh OSMLab imagery.json dowloaded')
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
    os.unlink('qms.json')
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

def find_qmsTMS(url):
    #   Search in qms for layer
    exist_qms = False
    layer = None
    for qmslayer in qmslist:
        if prepare_url(url) in qmslayer['url'].upper():
                exist_qms = True
                layer = qmslayer

    return layer, exist_qms

def find_qmsWMS(url,layers):
    #   Search in qms for layer
    exist_qms = False
    layer = None
    for qmslayer in qmslist:
        if prepare_url(url) in qmslayer['url'].upper() and qmslayer['type'] == 'wms':
            if qmslayer['layers'].upper() == layers.upper():
                exist_qms = True
                layer = qmslayer

    return layer, exist_qms

def find_changes(qmslayer,layer):
    find_changes = ''

    if len(qmslayer['desc'].split(':')) > 1 and layer['id'] == qmslayer['desc'].split(':')[1].split('. ')[0].strip():
        #this service is synced with OSMLab
        if 'license_url' in layer.keys() and layer['license_url'] != qmslayer['license_url'] and layer['license_url'] != 'Public Domain':
            find_changes = find_changes + ';' + 'license_url'
        if len(qmslayer['desc'].split(':')) >2:
            cntry = [x for x in countryinfo.countries if x['name'] == qmslayer['desc'].split(':')[2].strip()]
            if layer['country_code'] != cntry[0]['code']:
                find_changes = find_changes + ';' + 'country'
        if layer['type'] != qmslayer['type']:
            find_changes = find_changes + ';' + 'type'    
        if 'attribution' in layer.keys():
            if 'text' in layer['attribution'].keys() and layer['attribution']['text'].strip() != qmslayer['copyright_text']:
                find_changes = find_changes + ';' + 'copyright_text'
            if 'url' in layer['attribution'].keys() and layer['attribution']['url'] != qmslayer['copyright_url']:
                find_changes = find_changes + ';' + 'copyright_url'
        if layer['name'] != qmslayer['name'] and layer['name'] + ' WMS' != qmslayer['name'] and layer['name'] + ' TMS' != qmslayer['name']:
            find_changes = find_changes + ';' + 'name'
        if 'extent' in layer.keys():
            if 'z_max' not in qmslayer.keys(): qmslayer['z_max'] = ''
            if 'z_min' not in qmslayer.keys(): qmslayer['z_min'] = ''
            if 'max_zoom' in layer['extent'].keys() and layer['extent']['max_zoom'] != qmslayer['z_max']:
                find_changes = find_changes + ';' + 'zmax'
            if 'min_zoom' in layer['extent'].keys() and layer['extent']['min_zoom'] != qmslayer['z_min']:
                find_changes = find_changes + ';' + 'zmin'
            
    return find_changes        
def url_osmlabTMS2qms(url):
    if 'switch' in url:
        regex = r'\{switch:.*?\}'
        pt = re.compile(regex)
        res = pt.search(url)
        switch = res.group(0)
        new_val =  switch.split(':')[1].split(',')[0]
        url = re.sub(regex,new_val,url)
    url = url.replace('{zoom}','{z}')
    url = url.replace('{zoom-1}','{z-1}')
    
    return url

def url_osmlabWMS2qms(url):
    url = url.split("?")[0]
    return url
    
def getLayersWMS(url):
    list = url.split("?")[1].split("&")
    params = dict(map(None,x.split('=')) for x in list)
    params = dict((k.upper(), v) for k,v in params.iteritems())
    layers = params['LAYERS']
    
    return layers

def getFormatWMS(url):
    list = url.split("?")[1].split("&")
    params = dict(map(None,x.split('=')) for x in list)
    params = dict((k.upper(), v) for k,v in params.iteritems())
    format = ''
    if 'FORMAT' in params:
        format = params['FORMAT']
    
    return format
    
def getParamsWMS(url):
    list = url.split("?")[1].split("&")
    params = dict(map(None,x.split('=')) for x in list)
    params = dict((k.upper(), v) for k,v in params.iteritems())
    getparams = ''
    for param in params:
        if param != 'LAYERS' and param != 'FORMAT' and params[param] != '':
            getparams = getparams + '&' + param + '=' + params[param]
    return getparams
    
if __name__ == '__main__':

    if not os.path.exists('qms_full.json') or args.update: downloadQMS('qms.json')
    if not os.path.exists('imagery.json') or args.update: downloadOSMLab('imagery.json')

    data = openjson('imagery.json')
    qmslist=openjson('qms_full.json')
    
    fieldnames = ['id', 'name', 'type', 'exist_qms', 'changes_sync', 'url','url_qms','layers_qms','format_qms','getparams_qms','country_code','start_date','end_date','min_zoom','max_zoom','best','overlay','license_url','attribution_text','attribution_url','available_projections', 'source', 'description']
    
    with open('list.csv', 'wb') as csvfile:
        listwriter = csv.DictWriter(csvfile, fieldnames, delimiter=';',quotechar='"', quoting=csv.QUOTE_ALL)
        headers = {} 
        for n in fieldnames:
            headers[n] = n
        listwriter.writerow(headers)
    
        for layer in data:
            row=dict()
            row['type'] = layer.get('type')
            row['url'] = layer.get('url')
            print row['url']
            if row['type'] == 'tms':
                row['url_qms'] = url_osmlabTMS2qms(row['url'])
            elif row['type'] == 'wms':
                row['layers_qms'] = getLayersWMS(row['url'])
                row['format_qms'] = getFormatWMS(row['url'])
                row['getparams_qms'] = getParamsWMS(row['url']).lstrip('&')
                row['url_qms'] = url_osmlabWMS2qms(row['url']) + '?'

            #Check if services already exists in QMS based on it's url
            exist_qms = ''
            if row['type'] == 'tms':
                qmslayer,exist_qms = find_qmsTMS(row['url_qms'])
            elif row['type'] == 'wms':
                qmslayer,exist_qms = find_qmsWMS(row['url_qms'],row['layers_qms'])
            row['exist_qms'] = exist_qms

            row['id'] = layer.get('id')
            row['name'] = layer.get('name').encode('utf8')
            
                
            row['start_date'] = layer.get('start_date')
            row['end_date'] = layer.get('end_date')
            row['country_code'] = layer.get('country_code')
            row['best'] = layer.get('best')
            row['overlay'] = layer.get('overlay')
            row['license_url'] = layer.get('license_url')
            row['available_projections'] = layer.get('available_projections')
            row['source'] = 'https://github.com/osmlab/editor-layer-index/blob/gh-pages/imagery.geojson'

            cntry = [x for x in countryinfo.countries if x['code'] == row['country_code']]
            if len(cntry) != 0:
                description = 'This service is imported from OSMLab. OSMLab id: ' + row['id'] + '. Country: ' + cntry[0]['name']
            else:
                description = 'This service is imported from OSMLab. OSMLab id: ' + row['id']


            row['description'] = description

            if 'attribution' in layer:
                if 'text' in layer['attribution']:
                    row['attribution_text'] = layer['attribution']['text'].encode('utf8')            
            if 'attribution' in layer:
                if 'url' in layer['attribution']:
                    row['attribution_url'] = layer['attribution']['url'].encode('utf8')
            if 'extent' in layer:
                if 'max_zoom' in layer['extent']:
                    row['max_zoom'] = layer['extent']['max_zoom']
                if 'min_zoom' in layer['extent']:
                    row['min_zoom'] = layer['extent']['min_zoom']

            if exist_qms:
                changes_exist = find_changes(qmslayer,layer)
                row['changes_sync'] = changes_exist
            else:
                if find_noimport(row['id']): row['exist_qms'] = 'Skip'

            listwriter.writerow(row)
