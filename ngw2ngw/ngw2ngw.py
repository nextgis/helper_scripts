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
    cfg['ngw_login']        = config.ngw1_login
    cfg['ngw_password']     = config.ngw1_password
    processor1=ngw_synchroniser.ngw_synchroniser(cfg=cfg)


    cfg=dict()
    cfg['ngw_url']          = config.ngw2_url
    cfg['ngw_resource_id']  = config.ngw2_resource_id
    cfg['ngw_login']        = config.ngw2_login
    cfg['ngw_password']     = config.ngw2_password
    processor2=ngw_synchroniser.ngw_synchroniser(cfg=cfg)




    '''
    print 'Start synchronisation from '+args.filename+' to '+cfg['ngw_url'] + '/resource/'+cfg['ngw_resource_id']
    externalData=processor.openGeoJson(check_field = args.check_field,filename=args.filename)
    ngwData=processor.GetNGWData('pa',check_field = args.check_field)
    processor.synchronize(externalData,ngwData,check_field = args.check_field)
    '''
    dump1new=processor1.dumpLayer(config.ngw1_resource_id)
    quit()



    dump2new=processor.dumpLayer()
    changeset1=processor.compareDumps(dump1new,dump1old)
    changeset2=processor.compareDumps(dump2new,dump2old)

    #apply changeset from 1 to 2
    processor.applyChangeset(changeset1,layer2)    

    #apply changeset from 2 to 1
    processor.applyChangeset(changeset2,layer1)

    dump1old=processor.dumpLayer(layer1)
    dump2old=processor.dumpLayer(layer2)
    dump1old.save()
    dump2ols.save()