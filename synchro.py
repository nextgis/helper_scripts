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

from osgeo import ogr
from osgeo import osr

import urllib

import zipfile

class OOPTFederate:
    '''project70'''

    accounts = {}

    def __init__(self):

        
        ua_sources=['http://opengeo.intetics.com.ua/osm/pa/data/protected_area_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/national_park_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/nature_reserve_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/ramsar_sites_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/park_polygon.zip',
                    'http://opengeo.intetics.com.ua/osm/pa/data/nature_conservation_polygon.zip',


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



        tmpMiddeShape=os.path.join('tmp','ua-middle'+'.geojson')

        outShapefile = tmpMiddeShape
        print outShapefile
        outDriver = ogr.GetDriverByName("GeoJSON")
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)
        outDataSource = outDriver.CreateDataSource(outShapefile)
        outLayer = outDataSource.CreateLayer("out", geom_type=ogr.wkbMultiPolygon)



        codeField = ogr.FieldDefn("code", ogr.OFTString)
        outLayer.CreateField(codeField)

        codeField = ogr.FieldDefn("oopt_type", ogr.OFTString)
        outLayer.CreateField(codeField)

        codeField = ogr.FieldDefn("name", ogr.OFTString)
        outLayer.CreateField(codeField)

        for url in self.accounts['ua']['sources']:
            #print 'open url'+url

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

           


            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(shpFileName, 0) # 0 means read-only. 1 means writeable.

            # Check to see if shapefile is found.
            if dataSource is None:
                print 'Could not open %s' % (shpFileName)
            else:
                print 'Opened %s' % (shpFileName)
                layer = dataSource.GetLayer()
                featureCount = layer.GetFeatureCount()
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

            print 'start read'
            print ooptType

            for feature in layer:
                geom = feature.GetGeometryRef()
                #print geom.ExportToWkt()
                            # Create the feature and set values

                featureDefn = outLayer.GetLayerDefn()

                outfeature = ogr.Feature(featureDefn)

                outfeature.SetGeometry(geom)

                outfeature.SetField("code", 'ua')
                outfeature.SetField("oopt_type", ooptType)
                if feature.GetField("name") != None:
                    outfeature.SetField("name", feature.GetField("name"))
                if (geom.IsValid()):                
                    outLayer.CreateFeature(outfeature)
            

            # Close DataSource
            #inDataSource.Destroy()
            


            #clear data in web

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





            del layer
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
