# -*- coding: utf-8 -*-
# Project: Import to PostGIS all layers from ArcGIS Feature service.
# Author: Eduard Kazakov <ee.kazakov@gmail.com>
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

def esriFiledTypeToPg(type):
    if type == 'esriFieldTypeOID':
        return ogr.OFTInteger64
    if type == 'esriFieldTypeInteger':
        return ogr.OFTInteger64
    if type == 'esriFieldTypeSmallInteger':
        return ogr.OFTInteger
    if type == 'esriFieldTypeDouble' or type == 'esriFieldTypeSingle':
        return ogr.OFTReal
    if type == 'esriFieldTypeString' or type == 'esriFieldTypeGlobalID' or type == 'esriFieldTypeGUID' or type == 'esriFieldTypeXML':
        return ogr.OFTString
    if type == 'esriFieldTypeDate':
        return ogr.OFTDate
    return ''

def esriGeometryTypeToPg(type, has_z):
    if type == 'esriGeometryPoint':
        return ogr.wkbPointZM if has_z else ogr.wkbPoint
    if type == 'esriGeometryMultipoint':
        return ogr.wkbMultiPointZM if has_z else ogr.wkbMultiPoint
    if type == 'esriGeometryPolyline':
        return ogr.wkbLineStringZM if has_z else ogr.wkbLineString
    if type == 'esriGeometryPolygon':
        return ogr.wkbPolygonZM if has_z else ogr.wkbPolygon
    return ''

def process_layer(arcgis_url, layer, pg_host, pg_port, pg_user, pg_password, pg_dbname, prefix, replace=False):
    layer_id = layer['id']
    layer_url = arcgis_url + '/{}'.format(layer_id)
    layer_url_json = arcgis_url + '/{}?f=json'.format(layer_id)

    table_name = '%s_%s' % (prefix, layer_id)

    try:
        headers = {'Accept-Encoding': 'deflate'}
        ret = requests.get(layer_url_json, headers=headers)
        ret.raise_for_status()
        j = ret.json()
        layer_name = j['name']
        layer_desc = j['description']
        layer_copyright = j['copyrightText']
        fields = j['fields']
        display_field = j['displayField']
        new_fields = []

        for field in fields:
            field_type = esriFiledTypeToPg(field['type'])
            if field_type != '':
                new_field = ogr.FieldDefn (str(field['name']), esriFiledTypeToPg(field['type']))
                new_fields.append(new_field)

        geom_type = j['geometryType']
        # Disable z now
        has_z = False
        # has_z = j['hasZ']
        pg_geom_type = esriGeometryTypeToPg(geom_type, has_z)
        if pg_geom_type == '':
            print('Failed to get layer "{}" geometry type'.format(layer_url))
            return

    except Exception as e:
        print('Failed to get layer "{}" description. Error: {}'.format(layer_url, e))
        return

    # Open database
    try:
        pg_ds = gdal.OpenEx('PG:dbname=\'%s\' host=\'%s\' port=\'%s\' user=\'%s\' password=\'%s\'' % (pg_dbname, pg_host, pg_port, pg_user, pg_password), gdal.OF_VECTOR | gdal.OF_UPDATE)
    except Exception as e:
        print('Failed to open PostGIS database connection. Error: {}'.format(e))
        return

    if pg_ds is None:
        print('Failed to open PostGIS database connection')
        return


    # Create table
    try:
        if replace:
            pg_layer = pg_ds.CreateLayer(table_name, srs3857, geom_type = pg_geom_type, options = ['OVERWRITE=YES'])
        else:
            pg_layer = pg_ds.CreateLayer(table_name, srs3857, geom_type=pg_geom_type)
        pg_layer.CreateFields(new_fields)
    except Exception as e:
        print('Failed to create table in PostGIS. Error: {}'.format(e))
        return


    # Open ESRI Layer
    esri_url = 'ESRIJSON:{}/query?orderByFields=OBJECTID+ASC&outfields=*&f=json'.format(layer_url)
    esri_ds = gdal.OpenEx(esri_url, gdal.OF_READONLY, open_options=['FEATURE_SERVER_PAGING=YES'])
    if esri_ds is None:
        print('Failed to open ESRI datasource')
        return

    esri_layer = esri_ds.GetLayer(0)
    feat = esri_layer.GetNextFeature()
    i = 0
    while feat is not None:
        geom = feat.GetGeometryRef()
        geom.TransformTo(srs3857)

        result_feat = ogr.Feature(pg_layer.GetLayerDefn())

        result_feat.SetGeometry(geom)

        for field_desc in new_fields:
            field_name = field_desc.GetName()
            field_datatype = field_desc.GetTypeName()

            field_val = None

            if field_datatype == 'Integer64':
                field_val = feat.GetFieldAsInteger64(field_name)
            elif field_datatype == 'Integer':
                field_val = feat.GetFieldAsInteger(field_name)
            elif field_datatype == 'Real':
                field_val = feat.GetFieldAsDouble(field_name)
            elif field_datatype == 'String':
                field_val = feat.GetFieldAsString(field_name)
            elif field_datatype == 'Date':
                # Special hack as current driver not support DateTime
                curretn_val = int(feat.GetFieldAsString(field_name)) / 1000
                field_val = datetime.utcfromtimestamp(curretn_val).strftime('%Y-%m-%d %H:%M:%S')

            if field_val is not None:
                # Debug
                # print('set field {} with {}'.format(field_name, field_val))
                result_feat.SetField(field_name, field_val)

        try:
            pg_layer.CreateFeature(result_feat)
        except Exception as e:
            print('Failed to create feature #{} in PostGIS. Error: {}'.format(i, e))
            continue

        feat = esri_layer.GetNextFeature()
        i+=1

    esri_ds = None
    pg_ds = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create PostGIS tables from ArcGIS Feature service')
    parser.add_argument('-i', '--input', help='ArcGIS Feature service URL', required=True)
    parser.add_argument('--pg_host', help='PostGIS Host', required=True)
    parser.add_argument('--pg_port', help='PostGIS Port', required=True)
    parser.add_argument('--pg_user', help='PostGIS user name', required=True)
    parser.add_argument('--pg_password', help='PostGIS password', required=True)
    parser.add_argument('--pg_dbname', help='PostGIS Database name', required=True)
    parser.add_argument('--prefix', help='Prefix for new PostGIS tables', required=True)
    parser.add_argument('--replace', help='Use for replacing existing tables in PostGIS', dest='replace', action='store_true', required=False)
    parser.set_defaults(replace=True)

    args = parser.parse_args()

    # Get Feature service description
    url = args.input + '?f=json'
    try:
        headers = {'Accept-Encoding': 'deflate'}
        ret = requests.get(url, headers=headers)
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

    # Fill layers
    for layer in layers:
        process_layer(args.input, layer, args.pg_host, args.pg_port, args.pg_user, args.pg_password, args.pg_dbname, args.prefix, args.replace)

# Run example:
# python arcgis_featureservice2postgis.py -i http://gis-vo.volganet.ru/arcgis/rest/services/OpenData/Medicina_101/FeatureServer --pg_host sandbox.nextgis.com --pg_user demo --pg_password demo123 --pg_port 54321 --pg_dbname demo --prefix medicina_101 --replace
