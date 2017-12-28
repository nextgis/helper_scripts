#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#******************************************************************************
# shapefile_splitter.py
# ---------------------------------------------------------
# Split a shapefile into many and reproject to UTM zone taken from attributes table
# More: https://gitlab.com/nextgis_private/
#
# Usage: 
#      usage: shapefile_splitter.py [-h] --input INPUT --utm_field UTM_FIELD --id_field ID_FIELD
#      where:
#           -h           Show this help message and exit
#           input        Input shapefile name
# Examples:
#      python shapefile_splitter.py --id_field Zone_UTM --utm_field Zone_UTM --output_folder output --input boundary_145.shp
#
# Copyright (C) 2017 Maxim Dubinin (maxim.dubinin@nextgis.ru)
# Created: 24.10.2017
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
import os
os.environ["SHAPE_ENCODING"] = "UTF-8"
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input',type=str,required=True,help='Input shapefile name')
parser.add_argument('--output_folder',type=str,required=True,help='Output folder (will be created)')
parser.add_argument('--utm_field',type=str,required=True,help='UTM zone field name')
parser.add_argument('--id_field',type=str,required=True,help='ID field name')
args = parser.parse_args()


def extract_features(in_layer,id,geom_type):
    name = str(id)
    in_layer.SetAttributeFilter("%s = %s" % (args.id_field,id))
    print 'Filtered %s features for id %s' % (in_layer.GetFeatureCount(),id)

    source_crs = osr.SpatialReference()
    source_crs.ImportFromEPSG(4326)
    #get UTM zone and TODO city name
    first_feature = in_layer.GetNextFeature()
    target_crs_num = 32600 + int(first_feature.GetField(args.utm_field))
    target_crs = osr.SpatialReference()
    target_crs.ImportFromEPSG(target_crs_num)
    transform = osr.CoordinateTransformation(source_crs, target_crs)

    in_layer.ResetReading()

    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driverName )
    if drv is None:
        print "%s driver not available.\n" % driverName

    f_out = drv.CreateDataSource('%s\%s.shp' % (args.output_folder,name) )
    if f_out is None:
        print "Creation of output file failed.\n"
        sys.exit( 1 )

    out_layer = f_out.CreateLayer(name, None, geom_type)
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

def get_unique_ids(in_layer):
    ids = []
    for f in in_layer:
        val = f.GetField(args.id_field)
        if val not in ids: ids.append(val)

    in_layer.ResetReading()
    return ids

if __name__ == '__main__':
    ogrData = ogr.Open(args.input, 0 )
    if not os.path.exists(args.output_folder): os.mkdir(args.output_folder)
     
    if ogrData is None:
        print "ERROR: open failed"
        sys.exit( 1 )

    in_layer = ogrData.GetLayer()
    geom_type = in_layer.GetGeomType() #GetGeometryType()
    if in_layer is None:
        print "ERROR: can't access layer"
        sys.exit( 1 )

    ids = get_unique_ids(in_layer)
    print "Feature count", in_layer.GetFeatureCount()

    source_crs = osr.SpatialReference()
    source_crs.ImportFromEPSG(4326)

    for id in ids:
        extract_features(in_layer,id,geom_type)

    ogrData.Destroy()