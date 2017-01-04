#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Upload service definitions from CSV (pregenerated from OSMLAB) to QMS
# Author: Maxim Dubinin <maxim.dubinin@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>

import time
import pyautogui
import csv

def add_service_tms(name,url,description,source,prj,zmin,zmax,license_url,attribution_text,attribution_url):
    interval = 0.05

    #click new service
    pyautogui.moveTo(1500, 150)
    pyautogui.click()
    time.sleep(10)

    #select service
    pyautogui.moveTo(700, 500)
    pyautogui.click()
    time.sleep(10)

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
    #pyautogui.press('enter')

def add_service_wms(name,url,layers,description,source,prj,format,getparams,license_url,attribution_text,attribution_url):
    interval = 0.05

    #click new service
    pyautogui.moveTo(1500, 150)
    pyautogui.click()
    time.sleep(10)

    #select service
    pyautogui.moveTo(700, 500)
    pyautogui.click()
    time.sleep(10)

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
    #pyautogui.press('enter')
    raw_input("Press Enter to continue...")

if __name__ == '__main__':
    
    #read noimport list
    with open("noimport.txt") as f:
        noimport = f.readlines()
        noimport = [x.strip('\n') for x in noimport]
    
    f_csv = "list.csv"
    with open(f_csv, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')

        for row in csvreader:
            if row['id'] not in noimport:
                t = row['type']

                name = row['name']
                url = row['url_qms']
                layers = row['layers_qms']
                
                description = 'This service is imported from OSMLab. OSMLab id: ' + row['id']
                source = 'https://github.com/osmlab/editor-layer-index/blob/gh-pages/imagery.geojson'

                prjs = row['available_projections']
                prjs_arr = [i.split(':')[1] for i in prjs]

                if '3857' in prjs_arr:
                    prj = '3857'
                elif '4326' in prjs_arr:
                    prj = '4326'
                elif len(prjs_arr) == 0:
                    prj = '3857'
                else:
                    prj = prjs_arr[0]
                
                format = row['format_qms']
                getparams = row['getparams_qms']
                zmin = row['min_zoom']
                zmax = row['max_zoom']

                license_url = row['license_url']
                attribution_text = row['attribution_text']
                attribution_url = row['attribution_url']

                if t == 'tms':
                    add_service_tms(name,url,description,source,prj,zmin,zmax,license_url,attribution_text,attribution_url)
                elif t == 'wms':
                    add_service_wms(name,url,layers,description,source,prj,format,getparams,license_url,attribution_text,attribution_url)
                else:
                    continue


