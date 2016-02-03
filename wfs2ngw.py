#!/usr/bin/env python
# -*- coding: utf-8 -*-
# sync wfs layesr with ngw resources

from osgeo import ogr
from osgeo import osr

import json
import requests
import os
import pprint

wfs_url = 'http://0.0.0.0:8888/arcgis/services/WFS_Services/GeoDataServer/WFSServer?'

ngw_url = 'http://1.1.1.1/api/resource/'
ngw_creds = ('ngw_login', 'ngw_passwd')
timeout = 3
earthRadius = 6378137.0
delta = 0.00000001

wfs_names = ('layer1','layer2','layer3',)
ngw_resources = (576,577,578,)

check_field = 'OBJECTID'

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
    
    # compare geom
    return compareGeom(ngw_feature['geom'], wfs_feature['geom'])
    
def createPayload(wfs_feature):
    payload = {
        'geom': wfs_feature['geom'].ExportToWkt(),
        'fields': wfs_feature['fields']
    }
    return payload

if __name__ == '__main__':
        
    ds = ogr.Open('WFS:' + wfs_url)
    if ds is None:
        print 'did not managed to open WFS datastore'
        exit()

    for resid, name in (zip(ngw_resources, wfs_names)):	
        print "Proceed " + name + " ..."
        
        # get NGW array
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
            
        # get WFS array
    
        lyr = ds.GetLayerByName(name)	
        lyr.ResetReading()
        
        wfs_result = dict()
        
        for feat in lyr:
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
                            
            feat_defn = lyr.GetLayerDefn()
            wfs_fields = dict()    
            
            for i in range(feat_defn.GetFieldCount()):
                field_defn = feat_defn.GetFieldDefn(i)
                #if field_defn.GetName() == 'gml_id':
                #    continue
                                    
                if field_defn.GetName() == check_field:
                    check_field_val = feat.GetFieldAsInteger(i)  #GetFieldAsInteger64(i)
                
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
            
            wfs_result[check_field_val] = dict()        
            wfs_result[check_field_val]['id'] = check_field_val      
            wfs_result[check_field_val]['fields'] = wfs_fields
            wfs_result[check_field_val]['geom'] = mercator_geom
            
        # compare wfs_result and ngw_result
        for ngw_id in ngw_result:
            if ngw_id in wfs_result:
                if not compareFeatures(ngw_result[ngw_id], wfs_result[ngw_id]):
                    # update ngw feature
                    print 'update feature #' + str(ngw_id)
                    payload = createPayload(wfs_result[ngw_id])
                    req = requests.put(ngw_url + str(resid) + '/feature/' + str(ngw_id), data=json.dumps(payload), auth=ngw_creds)
            else:
                print 'delete feature #' + str(ngw_id)
                req = requests.delete(ngw_url + str(resid) + '/feature/' + str(ngw_id), auth=ngw_creds)
                
        # add new
        for wfs_id in wfs_result:
            if wfs_id not in ngw_result:
                print 'add new feature #' + str(wfs_id)
                payload = createPayload(wfs_result[ngw_id])
                req = requests.post(ngw_url + str(resid) + '/feature/', data=json.dumps(payload), auth=ngw_creds)
            
    ds = None 
