#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#******************************************************************************
# shp2shps.py
# ---------------------------------------------------------
# Convert each feature from a layer to reprojected layer with this feature
# More: https://gitlab.com/nextgis_private/
#
# Usage: 
#      usage: shp2shps.py [-h] input
#      where:
#           -h           Show this help message and exit
#           input        Input shapefile name
# Examples:
#      python shp2shps.py boundary_145.shp
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
parser.add_argument('input', help='Input shapefile name')
args = parser.parse_args()


def save_shp(in_layer,name,transform,in_feat):
    driverName = "ESRI Shapefile"
    drv = ogr.GetDriverByName( driverName )
    if drv is None:
        print "%s driver not available.\n" % driverName

    f_out = drv.CreateDataSource( "%s.shp" % name )
    if f_out is None:
        print "Creation of output file failed.\n"
        sys.exit( 1 )

    out_layer = f_out.CreateLayer( "name", None, ogr.wkbPolygon )
    if out_layer is None:
        print "Layer creation failed."
        sys.exit( 1 )

    inLayerDefn = in_layer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        out_layer.CreateField(fieldDefn)
    
    geom = f.GetGeometryRef()
    geom.Transform(transform)

    feat = ogr.Feature( out_layer.GetLayerDefn() )
    feat.SetGeometry(geom)

    outLayerDefn = out_layer.GetLayerDefn()
    for i in range(0, outLayerDefn.GetFieldCount()):
        feat.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), in_feat.GetField(i))

    if out_layer.CreateFeature( feat ) != 0:
        print "Failed to create feature in shapefile.\n"
        sys.exit( 1 )

    target_crs.MorphToESRI()
    file = open('%s.prj' % name.decode('utf-8'), 'w')
    file.write(target_crs.ExportToWkt())
    file.close()

    feat.Destroy()
    f_out.Destroy()


if __name__ == '__main__':
    ogrData = ogr.Open(args.input, 0 )
     
    if ogrData is None:
        print "ERROR: open failed"
        sys.exit( 1 )

    in_layer = ogrData.GetLayer()
    if in_layer is None:
        print "ERROR: can't access layer"
        sys.exit( 1 )

    print "Feature count", in_layer.GetFeatureCount()

    source_crs = osr.SpatialReference()
    source_crs.ImportFromEPSG(4326)
    for f in in_layer:
        target_crs_num = 32600 + int(f.GetFieldAsString(9)) #last field has UTM zone number
        target_crs = osr.SpatialReference()
        target_crs.ImportFromEPSG(target_crs_num)

        transform = osr.CoordinateTransformation(source_crs, target_crs)


        name = f.GetFieldAsString(0)
        print name
        save_shp(in_layer,name,transform,f)

    ogrData.Destroy()