# -*- coding: utf-8 -*-

#Open shapefile in zip
#Add field with area


from osgeo import ogr
import os

def calc_area():

        area_fieldname = 'Area'
        filename = "../states.shp"
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(filename, 0)
        layer = dataSource.GetLayer()

        #add field for area
        field_defenition = ogr.FieldDefn(area_fieldname,ogr.OFTString)
        layer.CreateField(field_denenition)

        frist_feature = layer.GetNextFeature()
        geometry = frist_feature.GetGeometryRef()
        layer.ResetReading()


        #reproject layers from 3857 to utm for area calc
        #layers should reprojected to utm before intersecting for more presision

        #get centroid of boundary
        centroid = geometry.Centroid()
        
        #reproject centroid from his CRS to 4326
        source = layer.GetSpatialRef()

        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)

        transform = osr.CoordinateTransformation(source, target)

        centroid.Transform(transform)
        #Get number of UTM zone for centroid using magic numbers 
        x = int(centroid.GetX() // 6)
        zone = x + 31
        epsg_utm = zone + 32600
        if int(centroid.GetX()) < 0 : 
            epsg_utm = zone + 32700 #south hemisphere
        
        logger.info("EPSG: %s" % (str(epsg_utm)))

        #reproject area from his CRS to UTM
        source = layer.GetSpatialRef()

        target = osr.SpatialReference()
        target.ImportFromEPSG(epsg_utm)

        transform = osr.CoordinateTransformation(source, target)
        geom_boundary_3857 = ogr.CreateGeometryFromWkt(boundary_wkt_geom)
        geom_boundary_3857.Transform(transform)
        geom_boundary_utm = geom_boundary_3857
        del geom_boundary_3857

        #walk by layer1 features
        
        for feature in layer:
            ngwFeatureId = feature['id']
            fields = feature['fields']
            
            geom_feature = feature.GetGeometryRef()
            geom_feature.Transform(transform)

            #calculate 
            total_area = geom_feature.GetArea()

            #write calc result to attribute
            feature.SetField(area_fieldname,str(total_area))


            
            #update features in ngw



layer.ResetReading()
