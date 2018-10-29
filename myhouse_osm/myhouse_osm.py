# -*- coding: utf-8 -*-

import os
from osgeo import ogr, osr, gdal

ogr.UseExceptions()

import argparse

def spatial_join(layer1, layer2):
    #layer1 - ogrlayer точки домов
    #layer2 - ogrlayer полигоны домов
    #returns two layer: matched and unmatched

    #=layer_matched. Create empty layer in memory
    layer_matched_driver=ogr.GetDriverByName('MEMORY')
    layer_matched_datasource=layer_matched_driver.CreateDataSource('memData')
    #open the memory datasource with write access
    tmp=layer_matched_driver.Open('memData',1)
    layer_matched = layer_matched_datasource.CreateLayer('layer_matched',
                            srs = layer1.GetSpatialRef(),
                            geom_type=layer1.GetLayerDefn().GetGeomType())
    # Add input Layer Fields to the memory Layer
    inLayerDefn = layer2.GetLayerDefn()
    for i in range(0, layer2.GetFieldCount()):
        fieldDefn = layer2.GetFieldDefn(i)
        layer_matched.CreateField(fieldDefn)
    inLayerDefn = None



    #=layer_unmatched. Create empty layer in memory
    layer_unmatched_driver=ogr.GetDriverByName('MEMORY')
    layer_unmatched_datasource=layer_unmatched_driver.CreateDataSource('memData')
    #open the memory datasource with write access
    tmp=layer_unmatched_driver.Open('memData',1)
    layer_unmatched = layer_unmatched_datasource.CreateLayer('layer_matched',
                            srs = layer2.GetSpatialRef(),
                            geom_type=layer2.GetLayerDefn().GetGeomType())
    # Add input Layer Fields to the memory Layer
    inLayerDefn = layer1.GetLayerDefn()
    for i in range(0, layer1.GetFieldCount()):
        fieldDefn = layer1.GetFieldDefn(i)
        layer_unmatched.CreateField(fieldDefn)
    inLayerDefn = None
    #оказалось что этот алгоритм нужно реализовывать самому

    layer1_feature_count = layer1.GetFeatureCount()
    layer2_feature_count = layer2.GetFeatureCount()

    for feature2 in layer1:
        geom2 = feature2.GetGeometryRef()
        for feature1 in layer1:
            if geom2.Intersects(geom1.GetGeometryRef()):
                outFeature = ogr.Feature(matched_layerdef)
                outFeature.SetGeometry(feature1)
                for i in range(feature2.GetFieldCount()):
                    outFeature.CreateField(feature2.GetFieldDefnRef(i))
                layer_matched.CreateFeature(outFeature)
                outFeature = None
            else
                outFeature = ogr.Feature(matched_layerdef)
                outFeature.SetGeometry(feature1)
                for i in range(feature2.GetFieldCount()):
                    outFeature.CreateField(feature2.GetFieldDefnRef(i))
                layer_unmatched.CreateFeature(outFeature)
                outFeature = None

    return layer_matched, layer_unmatched



def attrs2polys(points_filename, polygons_filename, result_filename='result.gpkg'):
    #spatial join of point and polygon layer with snapping point to neat feature

    #work in 3857
    filename = "../spatialite/working.gpkg"
    layername = 'myhouse'
    driver_point = ogr.GetDriverByName("GPKG")
    points_datasource = driver_point.Open(filename, 0)
    points_layer = points_datasource.GetLayer(layername)
    #open points layer, copy features to MEMORY
    layer1_driver=ogr.GetDriverByName('MEMORY')
    layer1_datasource=layer1_driver.CreateDataSource('memData')
    #open the memory datasource with write access
    tmp=layer1_driver.Open('memData',1)
    layer1=layer1_datasource.CopyLayer(points_datasource.GetLayer(),'layer1',['OVERWRITE=YES'])

    filename = "../building-polygon.shp"
    layername = 'building-polygon'
    driver_polygons = ogr.GetDriverByName("ESRI Shapefile")
    polygons_datasource = driver_polygons.Open(filename, 0)
    points_layer = polygons_datasource.GetLayer(layername)
    #open points layer, copy features to MEMORY
    layer2_driver=ogr.GetDriverByName('MEMORY')
    layer2_datasource=layer2_driver.CreateDataSource('memData')
    #open the memory datasource with write access
    tmp=layer2_driver.Open('memData',1)
    layer2=layer2_datasource.CopyLayer(points_datasource.GetLayer(),'layer2',['OVERWRITE=YES'])

    join_1pass, unmatched_1pass = spatial_join(layer1,layer2)
    



    buffer_1st_pass = buffer(buildings)
    #actually тут должен делаться буфер, затем из буферов от building=apartments вычитаться буфера от building=yes,
    #тогда если точка попадёт в буфер и жилого дома и магазина, то она притянется к жилому дому

    join_2pass, unmatched_2pass = spatial_join(unmatched_1pass,buffer_1st_pass)
    buffer_2st_pass = buffer(buffer_1st_pass)

    join_3pass, unmatched_3pass = spatial_join(unmatched_2pass,buffer_2st_pass)

    result_layer = join_layers([join_1pass,join_2pass,join_3pass])
