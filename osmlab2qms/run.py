#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Two-directional synchrosnisation of 2 ngw layers
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>







#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
from pprint import pprint
import os
import urlparse
import re


def import_qms1():
    url='https://qms.nextgis.com/api/v1/geoservices/?format=json'
    filename='qms.json'
    testfile = urllib.URLopener()
    testfile.retrieve(url, filename)


    #response = urllib.urlopen(url)
    #data = json.loads(response.read())
    with open(filename) as data_file:    
        data = json.load(data_file)
    #read intomemory
    return data

def downloadqms():
    qmslist=import_qms1()
    newlist=[]
    os.unlink('qms.json')
    for layer in qmslist:

        url='https://qms.nextgis.com/api/v1/geoservices/'+str(layer['id'])+'/?format=json'
        print url
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        layer.update(data)

        #print layer
        newlist.append(layer)
        with open('qms.json', 'wb') as outfile:
            json.dump(newlist, outfile)

    quit('теперь закомментируйте вызов downloadqms() и перезапускайте')        

def openqmsfile():

    with open('qms.json') as data_file:    
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



if __name__ == '__main__':


    #downloadqms()
    qmslist=openqmsfile()
    
    #read file from github
    url='https://raw.githubusercontent.com/osmlab/editor-layer-index/gh-pages/imagery.json'
    filename='imagery.json'


    with open('imagery.json') as data_file:    
        data = json.load(data_file)
    #read intomemory


    import csv
    fieldnames = ['name', 'type', 'url','likely_already_qms','likely_qms_layers', 'overlay','license_url','attribution_text','attribution_url','available_projections','id']
    with open('validator.csv', 'wb') as csvfile:
        spamwriter = csv.DictWriter(csvfile, fieldnames, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_ALL)

    #pprint(data)
        headers = {} 
        for n in fieldnames:
            headers[n] = n
        spamwriter.writerow(headers)

        for layer in data:


            #   Search in qms for layer with same domain
           
            osmlab_layer_domain=getLayerDomain(layer.get('url'))
            likely_already_qms = False
            likely_qms_layers = []
            for qmslayer in qmslist:
                print qmslayer
                if qmslayer['type'].upper() == layer.get('type').upper():
                    if getLayerDomain(qmslayer['url']) == getLayerDomain(layer.get('url')):
                        likely_already_qms = True
                        likely_qms_layers.append(qmslayer['url'])


            #   /Search
                    




            row=dict()
            row['id'] = layer.get('id')
            row['name'] = layer.get('name').encode('utf8')
            row['type'] = layer.get('type')
            row['overlay'] = layer.get('overlay')
            row['url'] = layer.get('url')
            row['license_url'] = layer.get('license_url')
            row['likely_already_qms'] = likely_already_qms
            row['likely_qms_layers'] = likely_qms_layers
            row['available_projections'] = layer.get('available_projections')
            if 'attribution' in layer:
                if 'text' in layer['attribution']:
                    row['attribution_text'] = layer['attribution']['text'].encode('utf8')            
            if 'attribution' in layer:
                if 'url' in layer['attribution']:
                    row['attribution_url'] = layer['attribution']['url'].encode('utf8')
            #print layer
            #quit()
            #row['attribution_text'] = layer.get('attribution',{'text':''}).get('text')
            #row['attribution_url'] = layer.get('attribution').get('url')




            spamwriter.writerow(row)

    #print list to screen