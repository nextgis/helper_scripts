#!/usr/bin/env python
# -*- coding: utf-8 -*-
#******************************************************************************
#
# grid.py
# ---------------------------------------------------------
# Upload images to a Web GIS
# More: https://gitlab.com/nextgis/helper_scripts
#
# Usage:
#      grid.py [-h] [-o] [-of ORIGINALS_FOLDER]
#      where:
#           -h              show this help message and exit
#           -o              overwrite
#           -of             relative path to folder with originals
#           -t              type of data, license or gin
# Example:
#      python grid.py -s 100 src.geojson dst.gpkg 
#
# Copyright (C) 2019-present Artem Svetlov (artem.svetlov@nextgis.com)
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

import os, sys
import requests
import json
import urllib2
import argparse
from copy import deepcopy
from contextlib import closing
import datetime
from math import ceil

import shapely

import shapely.geometry
import shapely.wkt

from osgeo import ogr, osr



def get_args():
    epilog = '''Sample: '''
    epilog +=  '''
    python grid.py -s 100 src.geojson dst.gpkg  '''
    p = argparse.ArgumentParser(description="Generate grid of points into source polygons", epilog=epilog)

    p.add_argument('--step',required=False, default = 1000,help='Steps in meters')
    p.add_argument('--mode',required=False,choices=['point', 'rect'], default = 'point',help='Grid mode.')

    p.add_argument('src', help='Vector polygonal or multipolygonal file with boundaries. Any format, any projection.')
    p.add_argument('dest', help='Result file. Extension should be .gpkg or .shp')

    p.add_argument('--verbose', '-v', help='messages', action='store_true')
    #p.add_argument('--config', help='patch to config.py file',required=False)
    return p.parse_args()




def get_utm_zone(centroid):

    #magic numbers 
    x = int(centroid.GetX() // 6)
    zone = x + 31
    epsg_utm = zone + 32600
    if int(centroid.GetX()) < 0 : 
        epsg_utm = zone + 32700 #south hemisphere

    return epsg_utm


def process():

    args = get_args()
    '''

    #open boundary geometry
    inputfn = 'samples/boundaries.geojson'
    outputGridfn = 'samples/grid.geojson'
    outputDriverName = 'ESRI Shapefile'
    
    #debug defaults
    mode = 'point' #point,rect
    
    gridWidth = 1000
    gridHeight = 1000
    '''

    #-------------------------------------
    #use argparse

    gridWidth = float(args.step)
    gridHeight = float(args.step)

    mode = args.mode

    inputfn = args.src
    outputGridfn = args.dest


    filename, file_extension = os.path.splitext(outputGridfn)
    if file_extension.upper() == '.SHP':
        outputDriverName = 'ESRI Shapefile'
    elif file_extension.upper() == '.GPKG':
        outputDriverName = 'gpkg'
    else:
        raise AttributeError('Not supported output format. Extension should be .gpkg or .shp')
        quit()

    
    inputds = ogr.Open(inputfn)
    inLayer = inputds.GetLayer()
    #create output layer

    srcSpatialRef = inLayer.GetSpatialRef()

    # output SpatialReference
    wgs1984SpatialRef = osr.SpatialReference()
    wgs1984SpatialRef.ImportFromEPSG(4326)
    coordTrans = osr.CoordinateTransformation(srcSpatialRef, wgs1984SpatialRef)

    outDriver = ogr.GetDriverByName(outputDriverName)
    if os.path.exists(outputGridfn):
        os.remove(outputGridfn)
    outDataSource = outDriver.CreateDataSource(outputGridfn)
    if mode == 'rect':
        outLayer = outDataSource.CreateLayer(outputGridfn,wgs1984SpatialRef,geom_type=ogr.wkbPolygon)
    elif mode == 'point':
        outLayer = outDataSource.CreateLayer(outputGridfn,wgs1984SpatialRef,geom_type=ogr.wkbPoint)
    elif mode == 'point2':
        outLayer = outDataSource.CreateLayer(outputGridfn,wgs1984SpatialRef,geom_type=ogr.wkbPoint)
    featureDefn = outLayer.GetLayerDefn()

    

    


    
    for i in range(0, inLayer.GetFeatureCount()):
        # Get the input Feature
        inFeature = inLayer.GetFeature(i)
        geom = inFeature.GetGeometryRef()
        #reproject boundary geometry from any projection to 4326
        geom.Transform(coordTrans)
        # Get centroid
        centroid = geom.Centroid()


        #get utm zone 
        utm_srs = get_utm_zone(centroid)


        #reproject boundary feature to utm

        utmSpatialRef = osr.SpatialReference()
        utmSpatialRef.ImportFromEPSG(utm_srs)
        toUTMcoordTrans = osr.CoordinateTransformation(wgs1984SpatialRef, utmSpatialRef)
        geom.Transform(toUTMcoordTrans)

        fromUTMcoordTrans = osr.CoordinateTransformation(utmSpatialRef, wgs1984SpatialRef)

        #get extent of boundary_utm

        xmin, xmax, ymin, ymax = geom.GetEnvelope()
        
        #generate grid (copied from gdal cookbok)

        xmin = float(xmin)
        xmax = float(xmax)
        ymin = float(ymin)
        ymax = float(ymax)
        gridWidth = float(gridWidth)
        gridHeight = float(gridHeight)

        # get rows
        rows = ceil((ymax-ymin)/gridHeight)
        # get columns
        cols = ceil((xmax-xmin)/gridWidth)

        # start grid cell envelope
        ringXleftOrigin = xmin
        ringXrightOrigin = xmin + gridWidth
        ringYtopOrigin = ymax
        ringYbottomOrigin = ymax-gridHeight

         # create grid cells
        countcols = 0
        while countcols < cols:
            countcols += 1

            # reset envelope for rows
            ringYtop = ringYtopOrigin
            ringYbottom =ringYbottomOrigin
            countrows = 0

            while countrows < rows:
                countrows += 1
                if mode == 'rect_ogr':
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    ring.AddPoint(ringXleftOrigin, ringYtop)
                    ring.AddPoint(ringXrightOrigin, ringYtop)
                    ring.AddPoint(ringXrightOrigin, ringYbottom)
                    ring.AddPoint(ringXleftOrigin, ringYbottom)
                    ring.AddPoint(ringXleftOrigin, ringYtop)
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(ring)
                    poly.Transform(fromUTMcoordTrans)

                    # add new geom to layer
                    outFeature = ogr.Feature(featureDefn)
                    outFeature.SetGeometry(poly)
                    outLayer.CreateFeature(outFeature)
                    outFeature = None
                elif mode == 'point_ogr':
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    ring.AddPoint(ringXleftOrigin, ringYtop)
                    ring.AddPoint(ringXrightOrigin, ringYtop)
                    ring.AddPoint(ringXrightOrigin, ringYbottom)
                    ring.AddPoint(ringXleftOrigin, ringYbottom)
                    ring.AddPoint(ringXleftOrigin, ringYtop)
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(ring)
                    poly.Transform(fromUTMcoordTrans)
                    grid_object = ogr.Geometry(ogr.wkbPoint)
                    #print ring.ExportToWkt()
                    centroid = poly.Centroid()
                    grid_object.AddGeometry(centroid)

                    #print centroid.ExportToWkt()

                     # add new geom to layer
                    outFeature = ogr.Feature(featureDefn)
                    outFeature.SetGeometry(centroid)
                    outLayer.CreateFeature(outFeature)
                    outFeature = None

                elif mode == 'rect':
                    shapely_grid_object_uncut = shapely.geometry.box(ringXleftOrigin, ringYbottom, ringXrightOrigin, ringYtop)

                elif mode == 'point':

                    #shapely_grid_object_uncut = shapely.geometry.box(ringXleftOrigin, ringYbottom, ringXrightOrigin, ringYtop).centroid
                    shapely_grid_object_uncut = shapely.geometry.box(ringXleftOrigin, ringYbottom, ringXrightOrigin, ringYtop)

                #shapely_grid_object_uncut is UTM
                #calculate crop of grid object and boundary
                shapely_boundary_utm = shapely.wkt.loads(geom.ExportToWkt())

                #print shapely_boundary_utm.wkt

                clip_operator = 'touches' #coveredby, intersects, all

                shapely_grid_object_cutted = None
                if clip_operator == 'all':
                    shapely_grid_object_cutted = shapely_grid_object_uncut

                elif clip_operator == 'touches':
                    if shapely_grid_object_uncut.intersects(shapely_boundary_utm):
                        shapely_grid_object_cutted = shapely_grid_object_uncut

                elif clip_operator == 'intersection':
                      if shapely_grid_object_uncut.intersects(shapely_boundary_utm):
                        shapely_grid_object_cutted = shapely_grid_object_uncut.intersection(shapely_boundary_utm)


                #if grid object outside filter - it variable become None

                #add shapely_grid_object_cutted to layer, reproject to 4326
                if shapely_grid_object_cutted is not None:
                    #make centroid here, because it more flexible for clip algorytms
                    if mode == 'rect':
                        pass
                    elif mode == 'point':
                        shapely_grid_object_cutted = shapely_grid_object_cutted.centroid

                    ogr_geometry_grid_object = ogr.CreateGeometryFromWkt(shapely_grid_object_cutted.wkt)  
                    ogr_geometry_grid_object.Transform(fromUTMcoordTrans)
                    outFeature = ogr.Feature(featureDefn)
                    outFeature.SetGeometry(ogr_geometry_grid_object)
                    outLayer.CreateFeature(outFeature)
                    outFeature = None


                #print shapely_grid_object_uncut.wkt

                #use grid_object here
                # new envelope for next poly
                ringYtop = ringYtop - gridHeight
                ringYbottom = ringYbottom - gridHeight

            # new envelope for next poly
            ringXleftOrigin = ringXleftOrigin + gridWidth
            ringXrightOrigin = ringXrightOrigin + gridWidth

        #reproject grid to 4326

        #add grid features to outlayer



    # Save and close DataSources
    inDataSource = None
    outDataSource = None

process()