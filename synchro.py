#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Download geodata from some sources and put it into NGW
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>



'''
Для каждого сервера
    Выкачиваем всё с сервера
    Сливаем всё в один слой (geojson или memory)
    Выкачиваем из веба всё по этому источнику.
    Сверяем записи локальные и в вебе по атрибутам и по геометрии
        одинаковы - пропускаем
        не одинаковы - удалить и залить этот
        остались несравненные локальные запипи - появилось в локальном - залить этот  
    Сверяем записи в вебе и локальные:     
        есть в вебе, нет в локальном - удалилось в локальном - удалить на сервере



'''

import os
import tempfile

from osgeo import ogr, gdal
from osgeo import osr

import urllib

import zipfile
import sys

class OOPTFederate:
    '''project70'''

    accounts = {}


    #Taken from wfs2ngw.py
    def compareValues(ngw_value, wfs_value):
        if (ngw_value == '' or ngw_value == None) and (wfs_value == '' or wfs_value == None):
            return True
        
        if isinstance(ngw_value, float) and isinstance(wfs_value, float):              
            return abs(ngw_value - wfs_value) < delta 
            
        if ngw_value != wfs_value:      
            return False
        return True
        
    def comparePoints(ngw_pt, wfs_pt):
        return (abs(ngw_pt.GetX() - wfs_pt.GetX()) < delta) and (abs(ngw_pt.GetY() - wfs_pt.GetY()) < delta)
        
    def compareLines(ngw_line, wfs_line):
        if ngw_line.GetPointCount() != wfs_line.GetPointCount():
            return False
        for i in range(ngw_line.GetPointCount()):
            if not comparePoints(ngw_line.GetPoint(i), wfs_line.GetPoint(i)):
                return False
            
        return True
        
    def comparePolygons(ngw_poly, wfs_poly):
        if ngw_poly.GetGeometryCount() != wfs_poly.GetGeometryCount():
            return False
        for i in range(ngw_poly.GetPointCount()):
            if not comparePoints(ngw_poly.GetGeometryRef(i), wfs_poly.GetGeometryRef(i)):
                return False

        return True                 
        
    def compareGeom(ngw_geom, wfs_geom):    
        if ngw_geom.GetGeometryType() is ogr.wkbPoint:      
            return comparePoints(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbLineString:
            return compareLines(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbPolygon:
            return comparePolygons(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPoint:
            for i in range(ngw_geom.GetGeometryCount()):
                if not comparePoint(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiLineString:
            for i in range(ngw_geom.GetGeometryCount()):
                if not compareLines(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPolygon:
            for i in range(ngw_geom.GetGeometryCount()):
                if not comparePolygons(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        else:
            return True # this is unexpected

        return True     

    def compareFeatures(ngw_feature, wfs_feature):
        # compare attributes
        ngw_fields = ngw_feature['fields']
        wfs_fields = wfs_feature['fields']
        for ngw_field in ngw_fields:
            if not compareValues(ngw_fields[ngw_field], wfs_fields[ngw_field]):
                return False

    #Taken from wfs2ngw.py





    def __init__(self):

        
        ua_sources=['http://opengeo.intetics.com.ua/osm/pa/data/protected_area_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/national_park_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/nature_reserve_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/ramsar_sites_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/park_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/nature_conservation_polygon.zip',


]
        ua_sources=[                    'http://opengeo.intetics.com.ua/osm/pa/data/national_park_polygon.zip',



]

        #self.accounts='1'
        self.accounts={'ua':{'sources':ua_sources}}
        #self.accounts.ua.sources.push('http://opengeo.intetics.com.ua/osm/pa/data/protected_area_polygon.zip')
        #self.accounts.ua.sources.push('http://opengeo.intetics.com.ua/osm/pa/data/national_park_polygon.zip')

        

    def download_ngw_snapshot(self):
        ngwUrl='http://176.9.38.120/pa/resource/7'
        pass


    def synchro_ua(self):
        print 'synchro_ua'
        #print self.accounts
        #print self.accounts['ua']['sources']

        '''
        ExternalLayer   - raw data from external provider
        brokerLayer        - processed data from external provider in our format with our fields
        ngwLayer        - layer in ngw
        '''


        tmpMiddeShape=os.path.join('tmp','ua-middle'+'.geojson')
        tmpWebSnapshot=os.path.join('tmp','websnapshotUA'+'.geojson')

        #Login to WFS here
        gdal.SetConfigOption('GDAL_HTTP_USERPWD', 'administrator:admin')

        tmpMiddleFilename = tmpMiddeShape
        outDriver = ogr.GetDriverByName("GeoJSON")
        if os.path.exists(tmpMiddleFilename):
            outDriver.DeleteDataSource(tmpMiddleFilename)
        #outDataSource = outDriver.CreateDataSource(tmpMiddleFilename)
        outDataSource = ogr.GetDriverByName( 'Memory' ).CreateDataSource(tmpMiddleFilename)
        brokerLayer = outDataSource.CreateLayer("Processed data from external provider in our format with our fields", geom_type=ogr.wkbMultiPolygon)


        #Create fields in middle data
        codeField = ogr.FieldDefn("code", ogr.OFTString)
        brokerLayer.CreateField(codeField)

        codeField = ogr.FieldDefn("oopt_type", ogr.OFTString)
        brokerLayer.CreateField(codeField)

        codeField = ogr.FieldDefn("name", ogr.OFTString)
        brokerLayer.CreateField(codeField)

        #Download each zip
        for url in self.accounts['ua']['sources']:

            tempZipFile = tempfile.NamedTemporaryFile(prefix='report_', suffix='.zip', dir='/tmp', delete=True)
            print 'download ' + url
            urllib.urlretrieve (url, tempZipFile.name)
            print 'saved to '+tempZipFile.name

            UnzipFolder='tmpm'

            with zipfile.ZipFile(tempZipFile, "r") as z:
                z.extractall(UnzipFolder)

            for file in os.listdir(UnzipFolder):
                if file.endswith(".shp"):
                    shpFileName=os.path.join(UnzipFolder,file)
            print shpFileName

           

            #Open each zip
    
            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(shpFileName, 0) # 0 means read-only. 1 means writeable.

            # Check to see if shapefile is found.
            if dataSource is None:
                print 'Could not open %s' % (shpFileName)
            else:
                print 'Opened %s' % (shpFileName)
                ExternalLayer = dataSource.GetLayer()
                featureCount = ExternalLayer.GetFeatureCount()
                print "Number of features in %s: %d" % (os.path.basename(shpFileName),featureCount)

            #does external data valid?
            if (featureCount < 1):
                print "Number of features in %s: %d" % (os.path.basename(shpFileName),featureCount)
                return 1 

            #change_attrs
            #create new layer


            '''
            #deprecated generation of prj
            srcSpatialRef = layer.GetSpatialRef()
            print srcSpatialRef.ExportToWkt()
            srcSpatialRef.MorphToESRI()
            file = open(os.path.join('tmp',os.path.splitext(os.path.basename(shpFileName))[0]+'.prj'), 'w')
            file.write(srcSpatialRef.ExportToWkt())
            file.close()
            '''

            #Read data from shp

            if ('protected_area' in url): 
                ooptType='protected_area'
            if ('national_park' in url): 
                ooptType='national_park'
            if ('nature_reserve' in url): 
                ooptType='nature_reserve'
            if ('ramsar_site' in url): 
                ooptType='ramsar_site'
            if ('park_polygon' in url): 
                ooptType='park_polygon'
            if ('nature_conservation' in url): 
                ooptType='nature_conservation'



            for feature in ExternalLayer:
                geom = feature.GetGeometryRef()

                featureDefn = brokerLayer.GetLayerDefn()
                outfeature = ogr.Feature(featureDefn)
                outfeature.SetGeometry(geom)

                #Add our special field - oopt_type

                outfeature.SetField("code", 'ua')
                outfeature.SetField("oopt_type", ooptType)
                if feature.GetField("name") != None:
                    outfeature.SetField("name", feature.GetField("name"))
                if (geom.IsValid()):                
                    brokerLayer.CreateFeature(outfeature)

            #brokerLayer = None

            
            

           
            #Now we have ogr layer with all data from one server with our fields

            #Выкачиваем из веба всё по этому источнику.

            #Make ogr object - wfs connection to ngw - Get WFS layers and iterate over features
            #Filter ngw objects by source attribute - using OGR WFS filter 



            print 'Connecting to our storage NGW via WFS'
            wfs_drv = ogr.GetDriverByName('WFS')
            # Open the webservice
            url = 'http://176.9.38.120/pa'+'/api/resource/10/wfs'
            wfsLayerName='main'
            wfs_ds = wfs_drv.Open('WFS:' + url)
            if not wfs_ds:
                sys.exit('ERROR: can not open WFS datasource')
            else:
                pass
            ngwLayer = wfs_ds.GetLayerByName(wfsLayerName)
            ngwLayer.SetAttributeFilter("code = 'UA'")
            srs = ngwLayer.GetSpatialRef()
            print 'ngwLayer: %s, Features: %s, SR: %s...' % (ngwLayer.GetName(), ngwLayer.GetFeatureCount(), srs.ExportToWkt()[0:250])
            ngwFeatureCount=ngwLayer.GetFeatureCount()

            '''
    Сверяем записи локальные c вебом по атрибутам и по геометрии
        одинаковы - пропускаем
        не одинаковы - удалить и залить этот
        остались несравненные локальные запипи - появилось в локальном - залить этот  
    Сверяем записи в вебе и локальные:     
        есть в вебе, нет в локальном - удалилось в локальном - удалить на сервере
            '''

            #re-open middle layer
            #brokerLayer = outDataSource.GetLayer() #и вот тут ничего не делается
            brokerLayer.ResetReading()
            brokerFeatureCount=brokerLayer.GetFeatureCount()
    


            #print 'ngwLayer: %s, Features: %s, SR: %s...' % (brokerLayer.GetName(), brokerLayer.GetFeatureCount(), brokerLayer.GetSpatialRef().ExportToWkt())
            for o in xrange(0,brokerFeatureCount):
                brokerFeature=brokerLayer.GetNextFeature()
                print 'broker&& %s '% (brokerFeature.GetField("name"))
                # iterate over features wfs
                ngwLayer.ResetReading()
                for x in xrange(0, ngwFeatureCount):
                    ngwFeature = ngwLayer.GetNextFeature()
                    print ngwFeature.GetField("name")

                ngwFeature = None
                ngwFeatureCount = None

            




            #put data from shp to web

            
            #clear unzip dir
            WipeDir=False
            if (WipeDir==False):
                filelist = [ f for f in os.listdir(UnzipFolder) ]
                for f in filelist:
                    #print 'remove'+f
                    os.remove(os.path.join(UnzipFolder,f))
            #quit()

            dataSource.Destroy()





            del ngwLayer
        outDataSource.Destroy()



processor=OOPTFederate()
#processor.download_ngw_snapshot()
processor.synchro_ua()






 

 
#temp = tempfile.NamedTemporaryFile(prefix='report_', suffix='.html', dir='/tmp', delete=True)
 
#zip_file = temp.name
#(dirName, fileName) = os.path.split(zip_file)
#fileBaseName = os.path.splitext(fileName)[0]
#pdf_file = dirName + '/' + fileBaseName + '.pdf'
 
#print html_file
