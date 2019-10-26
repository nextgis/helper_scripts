#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Import to NextGIS Web all layers from ArcGIS Feature service. 
# Author: Dmitry Baryshnikov <dmitry.baryshnikov@nextgis.com>
# Copyright: 2019, NextGIS <info@nextgis.com>
# License: GNU GPL v2 or any later version

import argparse
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import requests
import json
from datetime import datetime

batch_size = 100

def fix_srs(srs):
    if int(gdal.VersionInfo('VERSION_NUM')) >= 3000000:
        try:
            srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        except:
            pass

srs3857 = osr.SpatialReference()
srs3857.ImportFromEPSG(3857)
fix_srs(srs3857)

def ngw_create_resource_url(host):
    return '{}/api/resource/'.format(host)

def create_resource_group(session, host, id, name, desc, meta):
    payload = {
        "resource": {
            "cls": "resource_group",
            "parent": { "id": id },
            "display_name": name,
            "description": desc,
        },
        "resmeta": {
            "items": meta
        }
    }
    try:
        response = session.post(ngw_create_resource_url(host), json.dumps(payload))
        ngw_response = response.json()
        return ngw_response['id']
    except: # Failed to create
        print(response.json())
        return -1    

def create_vector_layer(session, host, id, name, desc, meta, geometry_type, fields):
    payload = {
        "resource": {
            "cls": "vector_layer",
            "parent": { "id": id },
            "display_name": name,
            "description": desc,
        },
        "resmeta": {
            "items": meta
        },
        "vector_layer":{
            "srs":{ "id":3857 },
            "geometry_type": geometry_type,
            "fields": fields,
        }
    }
    try:
        response = session.post(ngw_create_resource_url(host), json.dumps(payload))
        ngw_response = response.json()
        return ngw_response['id']
    except: # Failed to create
        print(response.json())
        return -1    

def esriFiledTypeToNgw(type):
    if type == 'esriFieldTypeOID':
        return 'BIGINT'
    if type == 'esriFieldTypeInteger':
        return 'BIGINT'
    if type == 'esriFieldTypeSmallInteger':
        return 'INTEGER'
    if type == 'esriFieldTypeDouble' or type == 'esriFieldTypeSingle':
        return 'REAL'    
    if type == 'esriFieldTypeString' or type == 'esriFieldTypeGlobalID' or type == 'esriFieldTypeGUID' or type == 'esriFieldTypeXML':
        return 'STRING'
    if type == 'esriFieldTypeDate':
        return 'DATETIME'        
    return ''

def esriGeometryTypeToNgw(type, has_z):
    if type == 'esriGeometryPoint':
        return 'POINTZ' if has_z else 'POINT'
    if type == 'esriGeometryMultipoint':
        return 'MULTIPOINTZ' if has_z else 'MULTIPOINT'
    if type == 'esriGeometryPolyline':
        return 'LINESTRINGZ' if has_z else 'LINESTRING'
    if type == 'esriGeometryPolygon':
        return 'POLYGONZ' if has_z else 'POLYGON'
    return ''

def process_layer(layer_url, session, ngw_url, ngw_resource_group, ngw_user, ngw_password):
    url = layer_url + '?f=json' 
    try:
        ret = requests.get(url)
        ret.raise_for_status()

        j = ret.json()
        layer_name = j['name']
        layer_desc = j['description']
        layer_copyright = j['copyrightText']
        fields = j['fields']
        display_field = j['displayField']
        new_fields = []
        for field in fields:
            field_type = esriFiledTypeToNgw(field['type'])
            if field_type != '':
                new_fields.append({
                    'keyname': field['name'],
                    'datatype': esriFiledTypeToNgw(field['type']),
                    'display_name': field['alias'],
                    'label_field': True if field['name'] == display_field else False,
                    'grid_visibility': True,
                })
        geom_type = j['geometryType']
        # Disable z now
        has_z = False
        # has_z = j['hasZ']
    except Exception as e:
        print('Failed to get layer "{}" description. Error: {}'.format(layer_url, e))
        return

    meta = {
        'copyrightText': layer_copyright,
    }

    ngw_geom_type = esriGeometryTypeToNgw(geom_type, has_z)
    if ngw_geom_type == '':
        print('Failed to get layer "{}" geometry type'.format(layer_url))
        return

    layer_id = create_vector_layer(session, ngw_url, ngw_resource_group, layer_name, layer_desc, meta, ngw_geom_type, new_fields)

    # Open NGW Layer
    url = 'NGW:{}/resource/{}'.format(ngw_url, layer_id)
    ngw_ds = gdal.OpenEx(url, gdal.OF_UPDATE, open_options=['BATCH_SIZE={}'.format(batch_size), 'USERPWD={}'.format(ngw_user + ':' + ngw_password)])
    if ngw_ds is None:
        print('Failed to open NextGIS Web datasource')
        return
    ngw_layer = ngw_ds.GetLayer(0)

    # Open ESRI Layer
    url = 'ESRIJSON:{}/query?orderByFields=OBJECTID+ASC&outfields=*&f=json'.format(layer_url) 
    esri_ds = gdal.OpenEx(url, gdal.OF_READONLY, open_options=['FEATURE_SERVER_PAGING=YES'])
    if esri_ds is None:
        print('Failed to open ESRI datasource')
        return

    esri_layer = esri_ds.GetLayer(0)
    feat = esri_layer.GetNextFeature()
    while feat is not None:
        geom = feat.GetGeometryRef()
        geom.TransformTo(srs3857)

        result_feat = ogr.Feature(ngw_layer.GetLayerDefn())

        result_feat.SetGeometry(geom) 

        for field_desc in new_fields:
            field_name = field_desc['keyname'].encode("utf8")
            field_val = None
            if field_desc['datatype'] == 'BIGINT':
                field_val = feat.GetFieldAsInteger64(field_name)
            elif field_desc['datatype'] == 'INTEGER':
                field_val = feat.GetFieldAsInteger(field_name)
            elif field_desc['datatype'] == 'REAL':
                field_val = feat.GetFieldAsDouble(field_name)
            elif field_desc['datatype'] == 'STRING':
                field_val = feat.GetFieldAsString(field_name)
            elif field_desc['datatype'] == 'DATETIME':
                # Special hack as current driver not support DateTime
                curretn_val = int(feat.GetFieldAsString(field_name)) / 1000
                field_val = datetime.utcfromtimestamp(curretn_val).strftime('%Y-%m-%d %H:%M:%S')

#                field_val = feat.GetFieldAsDateTime(field_name)
            
            if field_val is not None:
                # Debug
                # print('set field {} with {}'.format(field_name, field_val))
                result_feat.SetField(field_name, field_val)

        ngw_layer.CreateFeature(result_feat)

        feat = esri_layer.GetNextFeature()

    esri_ds = None
    ngw_ds = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create restricted areas from NextGIS OSM extracts.')
    parser.add_argument('-i', '--input', help='ArcGIS Feature service URL', required=True)
    parser.add_argument('--ngw_url', help='NGW url', required=True)
    parser.add_argument('--ngw_user', help='NGW user name')
    parser.add_argument('--ngw_password', help='NGW password')
    parser.add_argument('--ngw_resource_group', type=int, help='NGW resource group identifier', default=0)

    args = parser.parse_args()

    # Get Feature service description
    url = args.input + '?f=json'
    try:
        ret = requests.get(url)
        ret.raise_for_status()

        j = ret.json()
        service_name = j['serviceDescription']
        service_desc = j['description']
        service_copyright = j['copyrightText']
        service_title = j['documentInfo']['Title']
        service_author = j['documentInfo']['Author']
        service_comments = j['documentInfo']['Comments']
        service_subject = j['documentInfo']['Subject']
        service_category = j['documentInfo']['Category']
        service_keywords = j['documentInfo']['Keywords']
        layers = j['layers']
    except Exception as e:
        exit('Failed to get service description. Error: {}'.format(e))

    # Create resoure group
    session = requests.Session()
    session.auth = (args.ngw_user, args.ngw_password)
    meta = {
        'copyrightText': service_copyright,
        'Title': service_title,
        'Author': service_author,
        'Comments': service_comments,
        'Subject': service_subject,
        'Category': service_category,
        'Keywords': service_keywords,
    }

    rg_id = create_resource_group(session, args.ngw_url, args.ngw_resource_group, service_name, service_desc, meta)
    if rg_id < 0:
        exit('Failed to create resource group {}'.format(service_name))

    # Fill layers
    for layer in layers:
        layer_id = layer['id']

        url = args.input + '/{}'.format(layer_id)

        process_layer(url, session, args.ngw_url, rg_id, args.ngw_user, args.ngw_password)
