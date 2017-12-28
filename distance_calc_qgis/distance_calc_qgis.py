#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#******************************************************************************
# distance_calc_qgis.py
# ---------------------------------------------------------
# Split a shapefile into many and for each calculate observed&estimated distance using QGIS Processing
# More: https://gitlab.com/nextgis_private/
#
# Usage: 
#      usage: distance_calc_qgis.py [-h] --input INPUT --utm_field UTM_FIELD --id_field ID_FIELD
#      where:
#           -h           Show this help message and exit
#           input        Input shapefile name
# Examples:
#      python distance_calc.py --utm_field UTM_zone --id_field ID_1 --output_folder output --input PublicStops_770_SJ.shp
#
# Copyright (C) 2017 Maxim Dubinin (maxim.dubinin@nextgis.ru)
# Created: 24.11.2017
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

from osgeo import ogr
from osgeo import osr

import sys
import time
import os
os.environ["SHAPE_ENCODING"] = "UTF-8"
import math
import platform

import qgis
from qgis.core import *
from PyQt4.QtGui import QApplication
import sys
app = QgsApplication([],False, None)

if platform.system() == 'Windows':
    sys.path.append('C:/NextGIS/share/ngqgis/python/plugins')
    app.setPrefixPath("C:/NextGIS", True)
    print QgsApplication.showSettings()
    QApplication.processEvents()
    #time.sleep(10)
    app.initQgis()
elif platform.system() == 'Linux':
    sys.path.append('/usr/share/ngqgis/python/plugins/')
    app.setPrefixPath("/usr", True)
    app.initQgis()
from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputHTML
from processing.core.outputs import OutputNumber
from processing.tools import dataobjects, vector

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input',type=str,required=True,help='Input shapefile name')
parser.add_argument('--output_folder',type=str,required=True,help='Output folder (will be created)')
parser.add_argument('--utm_field',type=str,required=True,help='UTM zone field name')
parser.add_argument('--id_field',type=str,required=True,help='ID field name')
args = parser.parse_args()

def extract_features(in_layer,id):
    name = str(id)
    in_layer.SetAttributeFilter("%s = %s" % (args.id_field,id))
    cnt = in_layer.GetFeatureCount()
    print 'Filtered %s features for id %s' % (cnt,id)

    source_crs = osr.SpatialReference()
    source_crs.ImportFromEPSG(4326)
    #get UTM zone and TODO city name
    first_feature = in_layer.GetNextFeature()
    target_crs_num = 32600 + int(first_feature.GetField(args.utm_field))
    target_crs = osr.SpatialReference()
    target_crs.ImportFromEPSG(target_crs_num)
    transform = osr.CoordinateTransformation(source_crs, target_crs)
    city_name = first_feature.GetField('city_1')

    in_layer.ResetReading()

    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driverName )
    if drv is None:
        print "%s driver not available.\n" % driverName

    f_out = drv.CreateDataSource('%s\%s.shp' % (args.output_folder,name) )
    if f_out is None:
        print "Creation of output file failed.\n"
        sys.exit( 1 )

    out_layer = f_out.CreateLayer(name, None, ogr.wkbPoint)
    if out_layer is None:
        print "Layer creation failed."
        sys.exit( 1 )

    outLayerDefn = out_layer.GetLayerDefn()

    for inFeature in in_layer:
        outFeature = ogr.Feature(outLayerDefn)

        geom = inFeature.GetGeometryRef()
        geom.Transform(transform)

        feat = ogr.Feature(outLayerDefn)
        feat.SetGeometry(geom)

        if out_layer.CreateFeature( feat ) != 0:
            print "Failed to create feature in shapefile.\n"
            sys.exit( 1 )

        feat.Destroy()

    f_out.Destroy()
    target_crs.MorphToESRI()
    file = open('%s/%s.prj' % (args.output_folder,name), 'w')
    file.write(target_crs.ExportToWkt())
    file.close()

    return city_name,cnt

def calculate_distances(id,city_name,cnt):
    layer = dataobjects.getObjectFromUri('%s/%s.shp' % (args.output_folder,id))
    spatialIndex = vector.spatialindex(layer)

    neighbour = QgsFeature()
    distance = QgsDistanceArea()

    sumDist = 0.00
    A = layer.extent()
    A = float(A.width() * A.height())

    features = vector.features(layer)
    count = len(features)
    total = 100.0 / count if count > 0 else 1
    for current, feat in enumerate(features):
        neighbourID = spatialIndex.nearestNeighbor(feat.geometry().asPoint(), 2)[1]
        request = QgsFeatureRequest().setFilterFid(neighbourID)
        neighbour = layer.getFeatures(request).next()
        sumDist += distance.measureLine(neighbour.geometry().asPoint(),feat.geometry().asPoint())

    do = float(sumDist) / count
    de = float(0.5 / math.sqrt(count / A))
    d = float(do / de)
    SE = float(0.26136 / math.sqrt(count ** 2 / A))
    zscore = float((do - de) / SE)

    print('do: %s, de: %s' % (do,de))
    
    write_result(str(id),city_name,cnt,str(do),str(de))

def write_result(id,city_name,cnt,do,de):
    s = '%s;%s;%s;%s;%s\n' % (id,city_name,cnt,do,de)
    f_csv.write(s)

def get_unique_ids(in_layer):
    ids = []
    for f in in_layer:
        val = f.GetField(args.id_field)
        if val not in ids: ids.append(val)

    in_layer.ResetReading()
    return ids

if __name__ == '__main__':
    if not os.path.exists(args.output_folder): os.mkdir(args.output_folder)

    ogrData = ogr.Open(args.input, 0 )
    f_csv = open('%s/results.csv' % args.output_folder,'wb')
    f_csv.write('ID;NAME;COUNT;Dist_Obs_m;Dist_Est_m\n')
     
    if ogrData is None:
        print "ERROR: open failed, no layer named %s" % args.input
        sys.exit( 1 )

    in_layer = ogrData.GetLayer()
    if in_layer is None:
        print "ERROR: can't access layer"
        sys.exit( 1 )
    in_layer.SetAttributeFilter('%s > 0' % args.utm_field)

    cnt = in_layer.GetFeatureCount()
    print "Feature count", cnt

    ids = get_unique_ids(in_layer)

    for id in ids:
        #split by id
        city_name,cnt = extract_features(in_layer,id)
        if cnt > 1:
            calculate_distances(id,city_name,cnt)
        else:
            print("Less then 2 features, can't calculate distances")
            write_result(str(id),city_name,cnt,0,0)

    ogrData.Destroy()
    f_csv.close()