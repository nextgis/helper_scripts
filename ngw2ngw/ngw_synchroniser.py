#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Two-directional synchrosnisation of 2 ngw layers
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>




import requests
import sys
import os
import json
from osgeo import ogr, gdal
from osgeo import osr
import urllib2

class ngw_synchroniser:


    accounts = {}

    def __init__(self,cfg):

        self.ForceToMultiGeom = False #В ngw api v2 надо было ставить True, но эта версия больше не поддерживается, поэтому всегда False
        self.delta = 0.00000001 #Using in compare points 
        self.ngw_url = cfg['ngw_url'] + '/api/resource/'
        self.ngw_root = cfg['ngw_url']
        self.resid=cfg['ngw_resource_id']
        self.ngw_creds = (cfg['ngw_creds'])

     #Taken from wfs2ngw.py
    def compareValues(self,ngw_value, local_value):
        if (ngw_value == '' or ngw_value == None) and (local_value == '' or local_value == None):
            return True
        
        if isinstance(ngw_value, float) and isinstance(local_value, float):              
            return abs(ngw_value - local_value) < self.delta 
            
        if ngw_value != local_value:      
            return False
        return True
        
    def comparePoints(self,ngw_pt, local_pt):
        return (abs(ngw_pt[0] - local_pt[0]) < self.delta) and (abs(ngw_pt[1] - local_pt[1]) < self.delta)
        
    def compareLines(self,ngw_line, local_line):
        if ngw_line.GetPointCount() != local_line.GetPointCount():
            return False
        for i in range(ngw_line.GetPointCount()):
            

            if not self.comparePoints(ngw_line.GetPoint(i), local_line.GetPoint(i)):
                return False
            
        return True
        
    def comparePolygons(self,ngw_poly, local_poly):
        ngw_poly_rings = ngw_poly.GetGeometryCount()
        local_poly_rings = local_poly.GetGeometryCount()
        if ngw_poly_rings != local_poly_rings:
            return False

        for i in range(ngw_poly_rings):
            if not self.compareLines(ngw_poly.GetGeometryRef(i), local_poly.GetGeometryRef(i)):
                return False 





        for i in range(ngw_poly.GetPointCount()):
            if not self.comparePoints(ngw_poly.GetGeometryRef(i), local_poly.GetGeometryRef(i)):
                return False

        return True                 
        
    def compareGeom(self,ngw_geom, local_geom):  


        if ngw_geom.GetGeometryCount() <> local_geom.GetGeometryCount():
            return False    #Diffirent geometry count
        elif ngw_geom.GetGeometryType() is ogr.wkbPoint:      
            return self.comparePoints(ngw_geom.GetPoint(), local_geom.GetPoint())  
        elif ngw_geom.GetGeometryType() is ogr.wkbLineString:
            return self.compareLines(ngw_geom, local_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbPolygon:
            return self.comparePolygons(ngw_geom, local_geom)  
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPoint:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.comparePoints(ngw_geom.GetGeometryRef(i).GetPoint(0), local_geom.GetGeometryRef(i).GetPoint(0)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiLineString:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.compareLines(ngw_geom.GetGeometryRef(i), local_geom.GetGeometryRef(i)):
                    return False
        elif ngw_geom.GetGeometryType() is ogr.wkbMultiPolygon:
            for i in range(ngw_geom.GetGeometryCount()):
                if not self.comparePolygons(ngw_geom.GetGeometryRef(i), local_geom.GetGeometryRef(i)):
                    return False
        else:

            return True # this is unexpected

        return True     

    def compareFeatures(self,ngw_feature, local_feature):
        # compare attributes
        ngw_fields = ngw_feature['fields']
        local_fields = local_feature['fields']
        for ngw_field in ngw_fields:
            if not self.compareValues(ngw_fields[ngw_field], local_fields[ngw_field]):
                return False
        # compare geom
        data = self.compareGeom(ngw_feature['geom'], local_feature['geom'])
        return data

    def createPayload(self,local_feature):
        payload = {
            'geom': local_feature['geom'].ExportToWkt(),
            'fields': local_feature['fields']
        }
        return payload

    def openGeoJson(self,check_field, filename):

        driver = ogr.GetDriverByName("GeoJSON")
        dataSource = driver.Open(filename, 0)
        layer = dataSource.GetLayer()


        local_result = dict()
        for feat in layer:
            
            #create geometry object
            geom = feat.GetGeometryRef()
            if geom is not None:
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(3857)
                geom_type = geom.GetGeometryType()
                geom.TransformTo(sr)
                
                if self.ForceToMultiGeom:
                    if geom_type == ogr.wkbLineString:
                        mercator_geom = ogr.ForceToLineString(geom)
                    elif geom_type == ogr.wkbPolygon:
                        mercator_geom = ogr.ForceToPolygon(geom)
                    elif geom_type == ogr.wkbPoint:
                        mercator_geom = ogr.ForceToMultiPoint(geom)
                    elif geom_type == ogr.wkbMultiPolygon:
                        mercator_geom = ogr.ForceToMultiPolygon(geom)
                    elif geom_type == ogr.wkbMultiPoint:
                        mercator_geom = ogr.ForceToMultiPoint(geom)
                    elif geom_type == ogr.wkbMultiLineString:
                        mercator_geom = ogr.ForceToMultiPolygon(geom)
                    else:            
                        mercator_geom = geom
                else:
                    mercator_geom = geom
            else:
                continue
            
            #Read broker fields


            feat_defn = layer.GetLayerDefn()
            local_fields = dict()    
            
            for i in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(i)
                #if field_defn.GetName() == 'gml_id':
                #    continue
                
                #Compare by one control field    
                                 
                if field_defn.GetName() == check_field:
                    check_field_val = feat.GetFieldAsString(i).decode('utf-8')  #GetFieldAsInteger64(i)
                    
                
                #Read fields
                if field_defn.GetType() == ogr.OFTInteger: #or field_defn.GetType() == ogr.OFTInteger64:
                    local_fields[field_defn.GetName()] = feat.GetFieldAsInteger(i) #GetFieldAsInteger64(i)
#                    print "%s = %d" % (field_defn.GetName(), feat.GetFieldAsInteger64(i))
                elif field_defn.GetType() == ogr.OFTReal:
                    local_fields[field_defn.GetName()] = feat.GetFieldAsDouble(i)
#                    print "%s = %.3f" % (field_defn.GetName(), feat.GetFieldAsDouble(i))
                elif field_defn.GetType() == ogr.OFTString:
#                    print "%s = %s" % (field_defn.GetName(), feat.GetFieldAsString(i))
                    local_fields[field_defn.GetName()] = feat.GetFieldAsString(i).decode('utf-8')
                else:
#                    print "%s = %s" % (field_defn.GetName(), feat.GetFieldAsString(i))
                    local_fields[field_defn.GetName()] = feat.GetFieldAsString(i).decode('utf-8')
            
            #Object with keys - as values of one control field
            local_result[check_field_val] = dict()        
            local_result[check_field_val]['id'] = check_field_val      
            local_result[check_field_val]['fields'] = local_fields
            local_result[check_field_val]['geom'] = mercator_geom.Clone()


        layer_result_sorted = dict()
        for key in sorted(local_result):
            layer_result_sorted[key]=local_result[key]



        return layer_result_sorted

    def layer2dict(self,check_field):
        '''
        Return dict with ngw_data, keys are values from check_field
        Renamed from GetNGWData
        '''
            
        #check_field = 'synchronisation_key
        # Put NGW records into array   

        req = requests.get(self.ngw_url + str(self.resid) + '/feature/', auth=self.ngw_creds)
        dictionary = req.json()

        ngw_result_sorted = self.ngw_result_sort(dictionary,check_field=check_field)

        return ngw_result_sorted

    def ngw_result_sort(self,json,check_field=None,useID=False):
        '''
        Take JSON-представление of ngw layer, return sorted dict. Uses in two synchronisation algoritms.
        Example:
            ngw_result_sorted = self.ngw_layer2dict(req.json(),check_field='some_attribute') returns dict with keys are values of attribute
            ngw_result_sorted = self.ngw_layer2dict(req.json(),useId=True) returns dict with keys are ngw id
        '''


        dictionary = json
        ngw_result = dict()
        geom_type = None
        for item in dictionary:
                if check_field:
                    objectid = item['fields'][check_field]
                elif useID:
                    objectid = item['id']
                else:
                    raise ValueError('You must specify for ngw_layer2dict [check_field] or [useID=True]')
                ngw_geom = ogr.CreateGeometryFromWkt(item['geom'])
                if geom_type is None:
                    geom_type = ngw_geom.GetGeometryType()

                #filter here

                ngw_result[objectid] = dict(
                    id = item['id'],
                    geom = ngw_geom,
                    fields = item['fields'],
                    extensions = item['extensions']
                )
                    
                #sort here
        ngw_result_sorted = dict()
        for key in sorted(ngw_result):
            ngw_result_sorted[key]=ngw_result[key]

        return ngw_result_sorted


    def synchronize(self,local_result, ngw_result, check_field):
        # compare local_result and ngw_result
        
        '''
        Compare ngw records with wfs
        if not compare: put to web (update)
        if ngw result not in wfs: delete from web
        
        Compare wfs records with ngw
        if wfs not in ngw: post to ngw (create)
        
        '''
        import pprint
        pp = pprint.PrettyPrinter()       


        #sort ngw_result
        ngw_result_sorted = dict()
        for key in ngw_result:
            ngw_result_sorted[ngw_result[key]['fields'][check_field]]=ngw_result[key]
        ngw_result = ngw_result_sorted

        #sort local_result
        local_result_sorted = dict()
        for key in local_result:
            local_result_sorted[local_result[key]['fields'][check_field]]=local_result[key]
        local_result = local_result_sorted

        for ngw_id in ngw_result:
            #ngwFeatureId=ngw_result[ngw_id]['fields'][check_field]
            ngwFeatureId=ngw_result[ngw_id]['id']

            #if ngw_id in local_result:
            if local_result.has_key(ngw_result[ngw_id]['fields'][check_field]):
                if not self.compareFeatures(ngw_result[ngw_id], local_result[ngw_id]):
                    # update ngw feature
                    
                    payload = self.createPayload(local_result[ngw_id])
                    req = requests.put(self.ngw_url + str(self.resid) + '/feature/' + str(ngwFeatureId), data=json.dumps(payload), auth=self.ngw_creds)
                    print 'update feature #' + str(ngw_id) + ' ' + str(req)
                #print 'same feature: '+str(ngw_id)
            else:
                print 'delete feature ' + str(ngw_id) + ' ngw_feature_id='+str(ngwFeatureId)
                req = requests.delete(self.ngw_url + str(self.resid) + '/feature/' + str(ngwFeatureId), auth=self.ngw_creds)
                
        # add new


        for local_id in local_result:
            #wfsFeatureId=local_result[local_id]['fields'][check_field]

            if local_id not in ngw_result:
                print 'add new feature #' + str(local_id)
                payload = self.createPayload(local_result[local_id])
                req = requests.post(self.ngw_url + str(self.resid) + '/feature/', data=json.dumps(payload), auth=self.ngw_creds)

    def layer2json(self,layer_id,filename):
        """Return all features from layer in NGW internal json format 


        """   
        try:
            req = requests.get(self.ngw_url + str(layer_id) + '/feature/',  auth=self.ngw_creds)
            req.raise_for_status()

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)


        return req.json()
        # Writing JSON data
        with open(filename, 'w') as f:
             json.dump(req.json(), f)

    def compareDumps(self,dumpnew,dumpold):
        import pprint
        pp = pprint.PrettyPrinter() 
        changeset=dict()
        changeset['DELETE']=list()
        changeset['POST']=list()

        ''' 
        Return a changeset for two JSON dumps of ngw layers created in diffrent times.
        Format will be maximum simlar to OSM changeset, because if often used
        '''
        #Проверяет сначала, вдруг переменные абсолютно одинаковы, тогда ничего делать не надо
        if dumpnew == dumpold:
            print 'Дампы одинаковые'
            return None
        #Потом как сравнивать? Можно по порядку каждую с каждой - но тогда из середины чего-нибудь удалится, и непонятно будет что делать.
        #Сравнивать можно по одинаковым id, ведь это сравнение новой версии слоя со старой.
        #Если у записей не совпадают геометрии, или не совпадают fields - то они считаются разными.
        #Дополнительно, у них могут не совпадать аттачменты.

        dumpnew_sorted = self.ngw_result_sort(dumpnew,useID=True)      
        dumpold_sorted = self.ngw_result_sort(dumpold,useID=True)      
        #Проходим по списку id из старого дампа, сравниваем каждую запись с записью с таким же id из нового.
        for old_id, old_feature in dumpold_sorted.iteritems():
            #Нельзя просто сравнить два куска json, потому что они хранятся как объекты gdal
          
            #Если в новом дампе не найдена запись с id из старого, значит в слое запись удалилась, добавляем в чейнджсет DELETE (содержимое записи из старого дампа)
            if (old_id not in dumpnew_sorted):
                print 'Feature ' + str(old_id) + ' deleted. DELETE'
                changeset_element = dict()
                changeset_element = dumpold_sorted[old_id]
                changeset['DELETE'].append(changeset_element)
                continue
            #Если переменные разные, - такая ситуация возникнуть не должна #значит в слое запись изменилась, то добавляем в чейнджсет PUT(запись из нового дампа). Если атачменты разные, то делаем запись чейнджсета по атачментам
            if (old_feature['extensions'] != dumpnew_sorted[old_id]['extensions']) or (old_feature['fields'] != dumpnew_sorted[old_id]['fields']) or (self.compareGeom(dumpold_sorted[old_id]['geom'],dumpnew_sorted[old_id]['geom']) == False):
                print 'Запись ' + str(old_id) + ' изменилась с прошлого запуска скрипта. Эта ситуация не предполагалась. Запись не трогается.' 

                

            #в чейнджсетах записываются данные записи а не их id
            #Если переменные одинаковы, то идём дальше. 
            else:
                print 'Feature ' + str(old_id) + ' not changed'
                continue
        #Проходим по списку id из нового дампа, сравниваем каждую запись с записью с таким же id из старого
        for new_id, new_feature in dumpnew_sorted.iteritems():
            #если в старом дампе нет id такого же как в новом, то добавляем в чейнджсет POST(содержимое записи)
            if (new_id not in dumpold_sorted):
                print 'Feature ' + str(old_id) + ' added. POST'
                changeset_element = dict()
                changeset_element = dumpnew_sorted[new_id]
                changeset['POST'].append(changeset_element)
                continue

        return changeset

    def applyChangeset(self,changeset,layer_id,source_ngw_url,source_layer_id):
        ''' 
        Apply changeset for layer. Make REST calls.
        
        В метод поступает id слоя и чейнджсет - набор изменений другого слоя
        '''
        import pprint
        pp = pprint.PrettyPrinter() 
        if (changeset == None):
            return 0
        #Записей PUT по условиям задания в нём нет
        #Если запись POST
        #Проходим по чейнджсету
        if (changeset['POST'] != None):
            for feature in changeset['POST']:
                #Если есть атачменты
                if (feature['extensions']['attachment'] != None):
                    #Проходим по списку атачментов
                    for attachment in feature['extensions']['attachment']:
                        print 'upload attachment ' + attachment['name']
                        attachment_url=source_ngw_url + '/api/resource/' + source_layer_id + '/feature/' + str(feature['id']) + '/attachment/' + str(attachment['id']) + '/download'
                        print attachment_url
                        headers = {'Content-type': 'multipart/form-data'}
                        files={'file':urllib2.urlopen(attachment_url)}
                        payload={
                            'file':'\tmp\test.file',
                            'name':'vaporwave'
                        }
                        print self.ngw_root + '/api/component/file_upload/upload'
                        req = requests.put(self.ngw_root + '/api/component/file_upload/upload',  files=files, auth=self.ngw_creds, headers=headers)
                        print req.json()

                        print 'Грузим атачмент, добавляем в массив json-ответ от сервера не реализовано'
                
                #Составляем payload с полями, добавляем атачмент
                #pp.pprint(feature)
                
                print 'create payload for POST'
                #use existing simple method
                payload = self.createPayload(feature)
                payload['extensions']=dict()
                print 'тут проверяем, нужно ли добавить к payload - атачменты'
                # append description
                # не работает, см. https://github.com/nextgis/nextgisweb/issues/543
                payload['extensions']['description'] = feature['extensions']['description']
                pp.pprint(payload)
                req = requests.post(self.ngw_url + str(layer_id) + '/feature/', data=json.dumps(payload), auth=self.ngw_creds)
                quit()

        #Если запись DELETE
        if (changeset['POST'] != None):
            print 'Получаем сейчас весь слой из веба, что бы найти в нём записи, которые надо удалить'
            #Находим через REST в слое запись с такими же полями и атрибутами.
            print 'Получаем GeoJSON'
            
            #Грохаем запись
            #В случае             


        
        return 0
