#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Two-directional synchrosnisation of 2 ngw layers
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>






import os


from osgeo import ogr, gdal
from osgeo import osr

import urllib


import sys
import requests
import pprint
import json
import config

import ngw_synchroniser



if __name__ == '__main__':


         
    cfg=dict()
    cfg['ngw_url']          = config.ngw1_url
    cfg['ngw_resource_id']  = config.ngw1_resource_id
    cfg['ngw_creds']        = config.ngw1_creds
    processor1=ngw_synchroniser.ngw_synchroniser(cfg=cfg)


    cfg=dict()
    cfg['ngw_url']          = config.ngw2_url
    cfg['ngw_resource_id']  = config.ngw2_resource_id
    cfg['ngw_creds']        = config.ngw2_creds
    processor2=ngw_synchroniser.ngw_synchroniser(cfg=cfg)




    '''
    print 'Start synchronisation from '+args.filename+' to '+cfg['ngw_url'] + '/resource/'+cfg['ngw_resource_id']
    externalData=processor.openGeoJson(check_field = args.check_field,filename=args.filename)
    ngwData=processor.GetNGWData('pa',check_field = args.check_field)
    processor.synchronize(externalData,ngwData,check_field = args.check_field)
    '''


    dump1new=processor1.layer2json(config.ngw1_resource_id,config.ngw1_dump_today_filename)
    # Writing JSON data
    with open(config.ngw1_dump_today_filename, 'w') as f:
         json.dump(dump1new, f)

    dump2new=processor2.layer2json(config.ngw2_resource_id,config.ngw2_dump_today_filename)
    # Writing JSON data
    with open(config.ngw2_dump_today_filename, 'w') as f:
         json.dump(dump2new, f)

  
    if os.path.isfile(config.ngw1_dump_yesterday_filename) and  os.path.isfile(config.ngw2_dump_yesterday_filename):


        with open(config.ngw1_dump_today_filename) as json_data:
            dump1old = json.load(json_data)

        with open(config.ngw2_dump_today_filename) as json_data:
            dump2old = json.load(json_data)

        changeset1=processor1.compareDumps(dump1new,dump1old)
        changeset2=processor1.compareDumps(dump2new,dump2old)

        #apply changeset from 1 to 2
        processor2.applyChangeset(changeset1,config.ngw2_resource_id)    

        #apply changeset from 2 to 1
        processor1.applyChangeset(changeset2,config.ngw1_resource_id)

    #save today dump as yesterday dump 

    os.rename(config.ngw1_dump_today_filename,config.ngw1_dump_yesterday_filename)
    os.rename(config.ngw2_dump_today_filename,config.ngw2_dump_yesterday_filename)
