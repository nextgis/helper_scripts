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
import requests
import pprint
import json

class OOPTFederate:
    '''project70'''

    accounts = {}


    #Taken from wfs2ngw.py
    def compareValues(self,ngw_value, wfs_value):
        if (ngw_value == '' or ngw_value == None) and (wfs_value == '' or wfs_value == None):
            return True
        
        if isinstance(ngw_value, float) and isinstance(wfs_value, float):              
            return abs(ngw_value - wfs_value) < delta 
            
        if ngw_value != wfs_value:      
            return False
        return True
        
    def comparePoints(self,ngw_pt, wfs_pt):
        return (abs(ngw_pt[0] - wfs_pt[0]) < self.delta) and (abs(ngw_pt[1] - wfs_pt[1]) < self.delta)
        
    def compareLines(self,ngw_line, wfs_line):
        if ngw_line.GetPointCount() != wfs_line.GetPointCount():
            return False
        for i in range(ngw_line.GetPointCount()):

            if not self.comparePoints(ngw_line.GetPoint(i), wfs_line.GetPoint(i)):
                return False
            
        return True
        
    def comparePolygons(self,ngw_poly, wfs_poly):
        ngw_poly_rings = ngw_poly.GetGeometryCount()
        wfs_poly_rings = wfs_poly.GetGeometryCount()
        if ngw_poly_rings != wfs_poly_rings:
            return False

        for i in range(ngw_poly_rings):
            if not self.compareLines(ngw_poly.GetGeometryRef(i), wfs_poly.GetGeometryRef(i)):
                return False 





        for i in range(ngw_poly.GetPointCount()):
            if not self.comparePoints(ngw_poly.GetGeometryRef(i), wfs_poly.GetGeometryRef(i)):
                return False

        return True                 
        
    def compareGeom(self,ngw_geom, wfs_geom):  
  
        if ngw_geom.GetGeometryCount() <> wfs_geom.GetGeometryCount():
            return False    #Diffirent geometry count
        elif ngw_geom.GetGeometryType() is ogr.wkbPoint:      
            return self.comparePoints(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbLineString:
            return self.compareLines(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbPolygon:
            return self.comparePolygons(ngw_geom, wfs_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPoint:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.comparePoint(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiLineString:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.compareLines(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPolygon:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.comparePolygons(ngw_geom.GetGeometryRef(i), wfs_geom.GetGeometryRef(i)):
                    return False
        else:

            return True # this is unexpected

        return True     

    def compareFeatures(self,ngw_feature, wfs_feature):
        # compare attributes
        ngw_fields = ngw_feature['fields']
        wfs_fields = wfs_feature['fields']
        for ngw_field in ngw_fields:
            if not self.compareValues(ngw_fields[ngw_field], wfs_fields[ngw_field]):
                return False
        # compare geom
        data=self.compareGeom(ngw_feature['geom'], wfs_feature['geom'])
        return data

    def createPayload(self,wfs_feature):
        payload = {
            'geom': wfs_feature['geom'].ExportToWkt(),
            'fields': wfs_feature['fields']
        }
        return payload

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

        self.ForceToMultiPolygon = False #Не знаю, нужно ли?
        self.delta = 0.00000001 #Using in compare points 

        

    def download_ngw_snapshot(self):
        ngwUrl='http://176.9.38.120/pa/resource/7'
        pass


    def synchro_ua(self):

    
        def DownloadAndUnzip(url):
            tempZipFile = tempfile.NamedTemporaryFile(prefix='report_', suffix='.zip', dir='/tmp', delete=True)

            urllib.urlretrieve (url, tempZipFile.name)


            UnzipFolder='tmpm'

            #Unzip to shapefile

            with zipfile.ZipFile(tempZipFile, "r") as z:
                z.extractall(UnzipFolder)

            for file in os.listdir(UnzipFolder):
                if file.endswith(".shp"):
                    shpFileName=os.path.join(UnzipFolder,file)

            return shpFileName



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
        codeField = ogr.FieldDefn("src_code", ogr.OFTString)
        brokerLayer.CreateField(codeField)

        codeField = ogr.FieldDefn("synchronisation_key", ogr.OFTString)
        brokerLayer.CreateField(codeField)

        codeField = ogr.FieldDefn("oopt_type", ogr.OFTString)
        brokerLayer.CreateField(codeField)

        codeField = ogr.FieldDefn("name", ogr.OFTString)
        brokerLayer.CreateField(codeField)

        #Download each zip
        for url in self.accounts['ua']['sources']:

            shpFileName = DownloadAndUnzip(url)
            #shpFileName = 'tmpm/protected_area_polygon.shp'

            #Open each Shapefile
    
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



            srcRecordCounter = 0
            for feature in ExternalLayer:
                srcRecordCounter = srcRecordCounter+1
                geom = feature.GetGeometryRef()
                if self.ForceToMultiPolygon == True:
                    if geom.GetGeometryType() == ogr.wkbPolygon:
                        geom = ogr.ForceToMultiPolygon(geom)

                featureDefn = brokerLayer.GetLayerDefn()
                outfeature = ogr.Feature(featureDefn)
                outfeature.SetGeometry(geom)

                #Add our special field - oopt_type

                outfeature.SetField("src_code", 'ua')
                outfeature.SetField("synchronisation_key", 'ua'+str(srcRecordCounter))
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

        ngw_url = 'http://176.9.38.120/pa/api/resource/'
        ngw_creds = ('administrator', 'admin')
        check_field = 'synchronisation_key'
        resid=12

        # Put NGW records into array   

        req = requests.get(ngw_url + str(resid) + '/feature/', auth=ngw_creds)
        dictionary = req.json()
        ngw_result = dict()
        geom_type = None
        for item in dictionary:
                objectid = item['fields'][check_field]
                ngw_geom = ogr.CreateGeometryFromWkt(item['geom'])
                if geom_type is None:
                    geom_type = ngw_geom.GetGeometryType()
                    
                ngw_result[objectid] = dict(
                    id=item['id'],
                    geom=ngw_geom,
                    fields=item['fields'],
                )
        pp = pprint.PrettyPrinter(indent=4)


        # Put broker records into array
        brokerLayer.ResetReading()
        wfs_result = dict()
        for feat in brokerLayer:
            
            #create geometry object
            geom = feat.GetGeometryRef()
            if geom is not None:
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(3857)
                geom.TransformTo(sr)
                
                if geom_type == ogr.wkbLineString:
                    mercator_geom = ogr.ForceToLineString(geom)
                elif geom_type == ogr.wkbPolygon:
                    mercator_geom = ogr.ForceToPolygon(geom)
                elif geom_type == ogr.wkbPoint:
                    mercator_geom = ogr.ForceToPoint(geom)
                elif geom_type == ogr.wkbMultiPolygon:
                    mercator_geom = ogr.ForceToMultiPolygon(geom)
                elif geom_type == ogr.wkbMultiPoint:
                    mercator_geom = ogr.ForceToMultiPoint(geom)
                elif geom_type == ogr.wkbMultiLineString:
                    mercator_geom = ogr.ForceToMultiPolygon(geom)
                else:            
                    mercator_geom = geom
            else:
                continue
            
            #Read broker fields
                            
            feat_defn = brokerLayer.GetLayerDefn()
            wfs_fields = dict()    
            
            for i in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(i)
                #if field_defn.GetName() == 'gml_id':
                #    continue
                
                #Compare by one control field    
                                 
                if field_defn.GetName() == check_field:
                    check_field_val = feat.GetFieldAsString(i).decode('utf-8')  #GetFieldAsInteger64(i)
                    
                
                #Read fields
                if field_defn.GetType() == ogr.OFTInteger: #or field_defn.GetType() == ogr.OFTInteger64:
                    wfs_fields[field_defn.GetName()] = feat.GetFieldAsInteger(i) #GetFieldAsInteger64(i)
#                    print "%s = %d" % (field_defn.GetName(), feat.GetFieldAsInteger64(i))
                elif field_defn.GetType() == ogr.OFTReal:
                    wfs_fields[field_defn.GetName()] = feat.GetFieldAsDouble(i)
#                    print "%s = %.3f" % (field_defn.GetName(), feat.GetFieldAsDouble(i))
                elif field_defn.GetType() == ogr.OFTString:
#                    print "%s = %s" % (field_defn.GetName(), feat.GetFieldAsString(i))
                    wfs_fields[field_defn.GetName()] = feat.GetFieldAsString(i).decode('utf-8')
                else:
#                    print "%s = %s" % (field_defn.GetName(), feat.GetFieldAsString(i))
                    wfs_fields[field_defn.GetName()] = feat.GetFieldAsString(i).decode('utf-8')
            
            #Object with keys - as values of one control field
            wfs_result[check_field_val] = dict()        
            wfs_result[check_field_val]['id'] = check_field_val      
            wfs_result[check_field_val]['fields'] = wfs_fields
            wfs_result[check_field_val]['geom'] = mercator_geom.Clone()



        # compare wfs_result and ngw_result
        
        '''
        Compare ngw records with wfs
        if not compare: put to web (update)
        if ngw result not in wfs: delete from web
        
        Compare wfs records with ngw
        if wfs not in ngw: post to ngw (create)
        
        '''


        for ngw_id in ngw_result:
            ngwFeatureId=ngw_result[ngw_id]['id']

            if ngw_id in wfs_result:
                if not self.compareFeatures(ngw_result[ngw_id], wfs_result[ngw_id]):
                    # update ngw feature
                    print 'update feature #' + str(ngw_id)
                    payload = self.createPayload(wfs_result[ngw_id])
                    req = requests.put(ngw_url + str(resid) + '/feature/' + str(ngwFeatureId), data=json.dumps(payload), auth=ngw_creds)
            else:
                print 'delete feature #' + str(ngw_id)
                req = requests.delete(ngw_url + str(resid) + '/feature/' + str(ngwFeatureId), auth=ngw_creds)
                
        # add new
        for wfs_id in wfs_result:
            wfsFeatureId=wfs_result[wfs_id]['id']
            if wfs_id not in ngw_result:
                print 'add new feature #' + str(wfs_id)
                payload = self.createPayload(wfs_result[wfs_id])

                req = requests.post(ngw_url + str(resid) + '/feature/', data=json.dumps(payload), auth=ngw_creds)

        quit()
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

                    os.remove(os.path.join(UnzipFolder,f))


        dataSource.Destroy()





        del ngwLayer
        outDataSource.Destroy()



processor=OOPTFederate()
processor.synchro_ua()

