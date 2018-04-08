#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Upload service definitions from CSV (pregenerated from OSMLAB, data.mos.ru etc.) to QMS
# Author: Maxim Dubinin <maxim.dubinin@nextgis.com>
# Copyright: 2016-present, NextGIS <info@nextgis.com>
# Run:
#       python csv2qms.py

import time
import pyautogui
import csv
import pyperclip

def add_service_tms(name,url,description,source,prj,zmin,zmax,origintop,license_url,attribution_text,attribution_url):
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

    #origintop
    if origintop == True:
        #pyautogui.press('tab')
        pyautogui.press('space')
    else:
        pyautogui.press('tab')

    #license_url
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

def add_service_geojson(name,url,description,source,prj,license_name,license_url,attribution_text,attribution_url,terms_url):
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
    pyperclip.copy(name.decode('utf-8'))
    pyautogui.hotkey("ctrl", "v")

    #enter service url
    pyautogui.press('tab')
    pyautogui.typewrite(url, interval=interval)

    #enter description
    pyautogui.press('tab')
    #pyautogui.typewrite(description, interval=interval)    
    pyperclip.copy(description.decode('utf-8'))
    pyautogui.hotkey("ctrl", "v")
    
    #enter source
    pyautogui.press('tab')
    #pyautogui.typewrite(source, interval=interval)
    pyperclip.copy(source.decode('utf-8'))
    pyautogui.hotkey("ctrl", "v")

    #projection
    pyautogui.press('tab')
    pyautogui.typewrite(prj, interval=interval)
    
    pyautogui.press('tab')
    pyautogui.press('enter')
    
    
    #license_name
    pyautogui.press('tab')
    pyperclip.copy(license_name.decode('utf-8'))
    pyautogui.hotkey("ctrl", "v")

    #license_url
    pyautogui.press('tab')
    pyautogui.typewrite(license_url, interval=interval)

    #attribution_text
    pyautogui.press('tab')
    #pyautogui.typewrite(attribution_text, interval=interval)
    pyperclip.copy(attribution_text.decode('utf-8'))
    pyautogui.hotkey("ctrl", "v")

    #attribution_url
    pyautogui.press('tab')
    pyautogui.typewrite(attribution_url, interval=interval)
    
    #terms_url
    pyautogui.press('tab')
    pyautogui.typewrite(terms_url, interval=interval)

    #OK
    pyautogui.press('tab')
    pyautogui.press('enter')

    #Save
    pyautogui.press('tab')
    pyautogui.press('enter')

    #additional enter in case licensing info was missing
    pyautogui.press('enter')
    #raw_input("Press Enter to continue...")

def add_geo(wkt):
    #TODO: Add polygon, only possible at the moment if QMS service ID is known, i.e. service already exists
    pass
    #cmd = ''
    #os.system(cmd)

if __name__ == '__main__':
    #buttons
    addservice_btn_x = 1800
    addservice_btn_y = 150
    addwms_btn_x = 1200
    addwms_btn_y = 600
    addtms_btn_x = 900
    addtms_btn_y = 600
    addgeojson_btn_x = 600
    addgeojson_btn_y = 600

    sleep = 15 #seconds
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

                prjs = row['available_projections']
                if prjs != '':
                    if ':' in prjs:
                        prjs_arr = [i.split(':')[1] for i in eval(prjs)]
                    else:
                        prjs_arr = eval(prjs)
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
                
                if t == 'tms' or t == 'wms':
                    layers = row['layers_qms']
                    imageformat = row['format_qms']
                    getparams = row['getparams_qms']
                    zmin = row['min_zoom']
                    zmax = row['max_zoom']
                    origintop = row['origintop']

                source = row['source']
                description = row['description']
                
                license_name = row['license_name']
                license_url = row['license_url']
                attribution_text = row['attribution_text']
                attribution_url = row['attribution_url']
                terms_url = row['terms_url']

                if t == 'tms':
                    add_service_tms(name,url,description,source,prj,zmin,zmax,origintop,license_url,attribution_text,attribution_url)
                    add_geo(row['osmlab_wkt'])
                    #print url
                elif t == 'wms':
                    add_service_wms(name,url,layers,description,source,prj,imageformat,getparams,license_url,attribution_text,attribution_url)
                    add_geo(row['osmlab_wkt'])
                    #print url
                elif t == 'geojson':
                    add_service_geojson(name,url,description,source,str(prj),license_name,license_url,attribution_text,attribution_url,terms_url)
                    #add_geo(row['osmlab_wkt'])
                else:
                    continue

                time.sleep(sleep)

