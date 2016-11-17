#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Two-directional synchrosnisation of 2 ngw layers
# Author: Artem Svetlov <artem.svetlov@nextgis.com>
# Copyright: 2016, NextGIS <info@nextgis.com>




import requests
import sys
import os
import json

class ngw_synchroniser:


    accounts = {}

    def __init__(self,cfg):

        self.ForceToMultiGeom = False #В ngw api v2 надо было ставить True, но эта версия больше не поддерживается, поэтому всегда False
        self.delta = 0.00000001 #Using in compare points 
        self.ngw_url = cfg['ngw_url']+'/api/resource/'
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

    def compareDumps(self,dump1new,dump1old):
        ''' 
        Return a changeset for two JSON dumps of ngw layers created in diffrent times.
        Format will be maximum simlar to OSM changeset, because if often used
        '''
        return 0

    def applyChangeset(self,changeset,layer_id):
        ''' 
        Apply changeset for layer. Make REST calls.
        '''
        return 0
