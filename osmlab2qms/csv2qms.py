#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Upload service definitions from CSV (pregenerated from OSMLAB, data.mos.ru etc.) to QMS
# Author: Maxim Dubinin <maxim.dubinin@nextgis.com>
# Copyright: 2016-present, NextGIS <info@nextgis.com>

import time
import pyautogui
import csv
import countryinfo

def add_service_tms(name,url,description,source,prj,zmin,zmax,license_url,attribution_text,attribution_url):
    #click new service
    pyautogui.moveTo(1500, 150)
    pyautogui.click()
    time.sleep(sleep)

    #select service
    pyautogui.moveTo(700, 500)
    pyautogui.click()
    time.sleep(sleep)

    #enter service name
    pyautogui.press('tab')
    pyautogui.typewrite(name, interval=interval)

    #enter service url
    pyautogui.press('tab')
    pyautogui.typewrite(url, interval=interval)

    #enter description
    pyautogui.press('tab')
    pyautogui.typewrite(description, interval=interval)    

    #enter source
    pyautogui.press('tab')
    pyautogui.typewrite(source, interval=interval)
    #pyautogui.scroll(-10)

    #projection
    pyautogui.press('tab')
    pyautogui.typewrite(prj, interval=interval)

    #minzoom
    pyautogui.press('tab')
    pyautogui.typewrite(zmin, interval=interval)

    #maxzoom
    pyautogui.press('tab')
    pyautogui.typewrite(zmax, interval=interval)

    #license_url
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.typewrite(license_url, interval=interval)

    #attribution_text
    pyautogui.press('tab')
    pyautogui.typewrite(attribution_text, interval=interval)

    #attribution_url
    pyautogui.press('tab')
    pyautogui.typewrite(attribution_url, interval=interval)

    #OK
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')

    #Save
    pyautogui.press('tab')
    pyautogui.press('enter')
    #raw_input("Press Enter to continue...")

def add_service_wms(name,url,layers,description,source,prj,imageformat,getparams,license_url,attribution_text,attribution_url):
    #click new service
    pyautogui.moveTo(1500, 150)
    pyautogui.click()
    time.sleep(sleep)

    #select service
    pyautogui.moveTo(900, 500)
    pyautogui.click()
    time.sleep(sleep)

    #enter service name
    pyautogui.press('tab')
    pyautogui.typewrite(name, interval=interval)

    #enter service url
    pyautogui.press('tab')
    pyautogui.typewrite(url, interval=interval)

    #enter layers
    pyautogui.press('tab')
    pyautogui.typewrite(layers, interval=interval)    

    #enter description
    pyautogui.press('tab')
    pyautogui.typewrite(description, interval=interval)    

    #enter source
    pyautogui.press('tab')
    pyautogui.typewrite(source, interval=interval)
    #pyautogui.scroll(-10)

    #projection
    pyautogui.press('tab')
    pyautogui.typewrite(prj, interval=interval)

    #image format
    pyautogui.press('tab')
    pyautogui.press('tab')

    imageformat = imageformat.split('/')[1].upper()
    ntabs = imageformats.index(imageformat) + 1

    for i in xrange(ntabs): pyautogui.press('tab')
    pyautogui.press('space')
    pyautogui.press('escape')

    #get params
    pyautogui.press('tab')
    pyautogui.typewrite(getparams, interval=interval)

    #license_url
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.typewrite(license_url, interval=interval)

    #attribution_text
    pyautogui.press('tab')
    pyautogui.typewrite(attribution_text, interval=interval)

    #attribution_url
    pyautogui.press('tab')
    pyautogui.typewrite(attribution_url, interval=interval)

    #OK
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')

    #Save
    pyautogui.press('tab')
    pyautogui.press('enter')
    #raw_input("Press Enter to continue...")

def add_service_geojson():


if __name__ == '__main__':
    sleep = 3 #seconds
    interval = 0.05
    imageformats = ['PNG','PNG8','PNG24','PNG32','GIF','BMP','JPEG','TIFF','TIFF8','GEOTIFF','GEOTIFF8','SVG']

    #read noimport list
    with open("noimport.txt") as f:
        noimport = f.readlines()
        noimport = [x.strip('\n') for x in noimport]
    
    f_csv = "list.csv"
    with open(f_csv, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')

        for row in csvreader:
            if row['id'] not in noimport and row['exist_qms'] == 'False' and len(row['url_qms']) < 500:
                t = row['type']

                name = row['name']
                print name
                url = row['url_qms']
                layers = row['layers_qms']
                
                cntry = [x for x in countryinfo.countries if x['code'] == row['country_code']]
                if len(cntry) != 0:
                    description = 'This service is imported from OSMLab. OSMLab id: ' + row['id'] + '. Country: ' + cntry[0]['name']
                else:
                    description = 'This service is imported from OSMLab. OSMLab id: ' + row['id']

                source = 'https://github.com/osmlab/editor-layer-index/blob/gh-pages/imagery.geojson'

                prjs = row['available_projections']
                if prjs != '':
                    prjs_arr = [i.split(':')[1] for i in eval(prjs)]
                else:
                    prjs_arr = []

                if '3857' in prjs_arr:
                    prj = '3857'
                elif '4326' in prjs_arr:
                    prj = '4326'
                elif len(prjs_arr) == 0:
                    prj = '3857'
                else:
                    prj = prjs_arr[0]
                
                imageformat = row['format_qms']
                getparams = row['getparams_qms']
                zmin = row['min_zoom']
                zmax = row['max_zoom']

                license_url = row['license_url']
                attribution_text = row['attribution_text']
                attribution_url = row['attribution_url']

                if t == 'tms':
                    add_service_tms(name,url,description,source,prj,zmin,zmax,license_url,attribution_text,attribution_url)
                    #print url
                elif t == 'wms':
                    add_service_wms(name,url,layers,description,source,prj,imageformat,getparams,license_url,attribution_text,attribution_url)
                    #print url
                elif t == 'geojson':
                    add_service_geojson(name,url,layers,description,source,prj,imageformat,getparams,license_url,attribution_text,attribution_url)
                else:
                    continue

                time.sleep(sleep)

