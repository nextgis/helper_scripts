#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Update a one layer in NextGIS Web from local geojson file
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>



'''

Update a one layer in NextGIS Web from local geojson file.
Before frist run you should create a layer from this file.




mkdir tmp
mkdir tmpm
'''

import os


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
            return abs(ngw_value - wfs_value) < self.delta 
            
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
        #pp = pprint.PrettyPrinter()       
        #pp.pprint(ngw_feature)
        #pp.pprint(wfs_feature)
        #quit()

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

        ua_sources=[                    'http://opengeo.intetics.com.ua/osm/pa/data/national_park_polygon.zip',



]
        
        ua_sources=['http://opengeo.intetics.com.ua/osm/pa/data/protected_area_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/national_park_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/nature_reserve_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/ramsar_sites_polygon.zip',
                    #'http://opengeo.intetics.com.ua/osm/pa/data/park_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/nature_conservation_polygon.zip',


]


        #self.accounts='1'
        self.accounts={'ua':{'sources':ua_sources}}
        #self.accounts.ua.sources.push('http://opengeo.intetics.com.ua/osm/pa/data/protected_area_polygon.zip')
        #self.accounts.ua.sources.push('http://opengeo.intetics.com.ua/osm/pa/data/national_park_polygon.zip')

        self.ForceToMultiPolygon = True #Не знаю, нужно ли?
        self.delta = 0.00000001 #Using in compare points 
        self.ngw_url = 'http://trolleway.nextgis.com/api/resource/'
        self.resid=6
        self.ngw_creds = ('administrator', 's8q9MKWk')

        

    def download_ngw_snapshot(self):
        ngwUrl='http://176.9.38.120/pa/resource/7'
        pass


    def GetExternalDataUA(self,check_field):

        def DownloadAndUnzip(url,UnzipFolder):
            #tempZipFile = tempfile.NamedTemporaryFile(prefix='report_', suffix='.zip', dir='/tmp', delete=True)
            tempZipFile='tmp/tmp.zip'
            urllib.urlretrieve (url, tempZipFile)
            #UnzipFolder='tmpm'

            #Unzip to shapefile

            with zipfile.ZipFile(tempZipFile, "r") as z:
                z.extractall(UnzipFolder)

            for file in os.listdir(UnzipFolder):
                if file.endswith(".shp"):
                    shpFileName=os.path.join(UnzipFolder,file)

            os.remove(os.path.join(tempZipFile))          



            print 'returning shape '+  shpFileName
            return shpFileName

        def CleanDir(UnzipFolder):
            WipeDir=True
            if (WipeDir==True):
                filelist = [ f for f in os.listdir(UnzipFolder) ]
                for f in filelist:
                    os.remove(os.path.join(UnzipFolder,f))
    



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
        srcRecordCounter = 0
        for url in self.accounts['ua']['sources']:
            print

            UnzipFolder='tmpm'
            CleanDir(UnzipFolder)

            print 'retrive '+url
            shpFileName = ''
            shpFileName = DownloadAndUnzip(url,UnzipFolder)
            print 'shpfilename'+shpFileName
            
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

            WipeDir=True
            if (WipeDir==False):
                filelist = [ f for f in os.listdir(UnzipFolder) ]
                for f in filelist:
                    os.remove(os.path.join(UnzipFolder,f))
            

           
            #Now we have ogr layer with all data from one server with our fields

            #Выкачиваем из веба всё по этому источнику.

            #Make ogr object - wfs connection to ngw - Get WFS layers and iterate over features
            #Filter ngw objects by source attribute - using OGR WFS filter 





        # Put broker records into array
        brokerLayer.ResetReading()
        wfs_result = dict()
        for feat in brokerLayer:
            
            #create geometry object
            geom = feat.GetGeometryRef()
            if geom is not None:
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(3857)
                geom_type = geom.GetGeometryType() #say to Dima
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


        #sort here
        wfs_result_sorted = dict()
        for key in sorted(wfs_result):
            wfs_result_sorted[key]=wfs_result[key]


        return wfs_result_sorted





    def openGeoJson0(self,check_field):

        print 'synchro_geojson'
        #print self.accounts
        #print self.accounts['ua']['sources']

        '''
        ExternalLayer   - raw data from external provider
        brokerLayer        - processed data from external provider in our format with our fields
        ngwLayer        - layer in ngw
        '''
    
        filename='routes_with_refs.geojson'


        driver = ogr.GetDriverByName("GeoJSON")
        dataSource = driver.Open(filename, 0)
        layer = dataSource.GetLayer()

        for feature in layer:
            print feature.GetField("STATE_NAME")


        wfs_names = ('Protected_Areas__federal__3',)
        outDataSource = ogr.GetDriverByName( 'Memory' ).CreateDataSource(os.path.join('tmp','pm'+'.geojson'))
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
        srcRecordCounter = 0
        for  name in  wfs_names:	
            print "Proceed " + name + " ..."

            ExternalLayer = ds.GetLayerByName(name)	
            ExternalLayer.ResetReading()

            for feature in ExternalLayer:
                srcRecordCounter = srcRecordCounter+1
                geom = feature.GetGeometryRef()
                if self.ForceToMultiPolygon == True:
                    geom = ogr.ForceToMultiPolygon(geom)

                featureDefn = brokerLayer.GetLayerDefn()
                outfeature = ogr.Feature(featureDefn)
                outfeature.SetGeometry(geom)

                #Add our special field - oopt_type

                outfeature.SetField("src_code", 'pm')
                outfeature.SetField("synchronisation_key", 'pm'+str(srcRecordCounter))
                outfeature.SetField("oopt_type", feature.GetField("Type_ru"))


                if feature.GetField("Name_ru") != None:
                    outfeature.SetField("name", feature.GetField("Name_ru"))

                if (geom.IsValid()):                
                    brokerLayer.CreateFeature(outfeature)


        #todo: put to separate method
        # Put broker records into array
        brokerLayer.ResetReading()
        wfs_result = dict()
        for feat in brokerLayer:
            
            #create geometry object
            geom = feat.GetGeometryRef()
            if geom is not None:
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(3857)
                geom_type = geom.GetGeometryType() #say to Dima
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


        #sort here
        wfs_result_sorted = dict()
        for key in sorted(wfs_result):
            wfs_result_sorted[key]=wfs_result[key]


        return wfs_result_sorted



    def openGeoJson(self,check_field, filename):


        #filename='routes_with_refs.geojson'


        driver = ogr.GetDriverByName("GeoJSON")
        dataSource = driver.Open(filename, 0)
        layer = dataSource.GetLayer()


        wfs_result = dict()
        for feat in layer:
            
            #create geometry object
            geom = feat.GetGeometryRef()
            if geom is not None:
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(3857)
                geom_type = geom.GetGeometryType() #say to Dima
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


            feat_defn = layer.GetLayerDefn()
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


        layer_result_sorted = dict()
        for key in sorted(wfs_result):
            layer_result_sorted[key]=wfs_result[key]


        #print layer_result_sorted
        #quit()
        return layer_result_sorted

    def GetNGWData(self,code,check_field):

        
        
        #check_field = 'synchronisation_key'
        

        # Put NGW records into array   

        req = requests.get(self.ngw_url + str(self.resid) + '/feature/', auth=self.ngw_creds)
        dictionary = req.json()
        ngw_result = dict()
        geom_type = None
        for item in dictionary:
                objectid = item['fields'][check_field]
                ngw_geom = ogr.CreateGeometryFromWkt(item['geom'])
                if geom_type is None:
                    geom_type = ngw_geom.GetGeometryType()

                #filter here

                ngw_result[objectid] = dict(
                    id=item['id'],
                    geom=ngw_geom,
                    fields=item['fields']
                )
                    
                #sort here
        ngw_result_sorted = dict()
        for key in sorted(ngw_result):
            ngw_result_sorted[key]=ngw_result[key]

 

        return ngw_result_sorted


    def synchronize(self,wfs_result, ngw_result, check_field):

        # compare wfs_result and ngw_result
        
        '''
        Compare ngw records with wfs
        if not compare: put to web (update)
        if ngw result not in wfs: delete from web
        
        Compare wfs records with ngw
        if wfs not in ngw: post to ngw (create)
        
        '''
        import pprint
        pp = pprint.PrettyPrinter()       
        #pp.pprint(ngw_result)
        #quit()   

        #print ngw_result
        #quit()

        #sort ngw_result
        ngw_result_sorted = dict()
        for key in ngw_result:
            ngw_result_sorted[ngw_result[key]['fields'][check_field]]=ngw_result[key]
        ngw_result = ngw_result_sorted

        #sort ngw_result
        wfs_result_sorted = dict()
        for key in wfs_result:
            wfs_result_sorted[wfs_result[key]['fields'][check_field]]=wfs_result[key]
        wfs_result = wfs_result_sorted





        for ngw_id in ngw_result:
            ngwFeatureId=ngw_result[ngw_id]['fields'][check_field]

            #if ngw_id in wfs_result:
            if wfs_result.has_key(ngwFeatureId):
                if not self.compareFeatures(ngw_result[ngw_id], wfs_result[ngw_id]):
                    # update ngw feature
                    print 'update feature #' + str(ngw_id)
                    payload = self.createPayload(wfs_result[ngw_id])
                    req = requests.put(self.ngw_url + str(self.resid) + '/feature/' + str(ngwFeatureId), data=json.dumps(payload), auth=self.ngw_creds)
            else:
                print 'delete feature ' + str(ngw_id) + ' ngw_feature_id='+str(ngwFeatureId)
                req = requests.delete(self.ngw_url + str(self.resid) + '/feature/' + str(ngwFeatureId), auth=self.ngw_creds)
                
        # add new

        for wfs_id in wfs_result:
            wfsFeatureId=wfs_result[wfs_id]['fields'][check_field]
            if wfs_id not in ngw_result:
                print 'add new feature #' + str(wfs_id)
                payload = self.createPayload(wfs_result[wfs_id])
                #print json.dumps(payload)
                req = requests.post(self.ngw_url + str(self.resid) + '/feature/', data=json.dumps(payload), auth=self.ngw_creds)

    

    

     



processor=OOPTFederate()
'''

'''
externalData=processor.openGeoJson(check_field = 'road_id',filename='routes_with_refs.geojson')
print 'fetch ngw data'
ngwData=processor.GetNGWData('pa',check_field = 'road_id')
print 'start sinchronisation'
processor.synchronize(externalData,ngwData,check_field = 'road_id')
