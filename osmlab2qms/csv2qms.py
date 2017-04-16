#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Upload service definitions from CSV (pregenerated from OSMLAB, data.mos.ru etc.) to QMS
# Author: Maxim Dubinin <maxim.dubinin@nextgis.com>
# Copyright: 2016-present, NextGIS <info@nextgis.com>

import time
import pyautogui
import csv

def add_service_tms(name,url,description,source,prj,zmin,zmax,license_url,attribution_text,attribution_url):
    #click new service
    pyautogui.moveTo(addservice_btn_x,addservice_btn_y)
    pyautogui.click()
    time.sleep(sleep)

    #select service
    pyautogui.moveTo(addtms_btn_x, addtms_btn_y)
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

    #addition enter in case licensing info was missing
    pyautogui.press('enter')
    #raw_input("Press Enter to continue...")

def add_service_wms(name,url,layers,description,source,prj,imageformat,getparams,license_url,attribution_text,attribution_url):
    #click new service
    pyautogui.moveTo(addservice_btn_x, addservice_btn_y)
    pyautogui.click()
    time.sleep(sleep)

    #select service
    pyautogui.moveTo(addwms_btn_x, addwms_btn_y)
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

    #addition enter in case licensing info was missing
    pyautogui.press('enter')

    #raw_input("Press Enter to continue...")

def add_service_geojson():
    #click new service
    pyautogui.moveTo(addservice_btn_x, addservice_btn_y)
    pyautogui.click()
    time.sleep(sleep)

    #select service
    pyautogui.moveTo(addgeojson_btn_x, addgeojson_btn_y)
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

    #addition enter in case licensing info was missing
    pyautogui.press('enter')
    #raw_input("Press Enter to continue...")


if __name__ == '__main__':
    #buttons
    addservice_btn_x = 1500
    addservice_btn_y = 170
    addwms_btn_x = 900
    addwms_btn_y = 500
    addtms_btn_x = 700
    addtms_btn_y = 500
    addgeojson_btn_x = 500
    addgeojson_btn_y = 500

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

                source = row['source']
                description = row['description']

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
                    #add_service_geojson(name,url,layers,description,source,prj,imageformat,getparams,license_url,attribution_text,attribution_url)
                    continue
                else:
                    continue

                time.sleep(sleep)

