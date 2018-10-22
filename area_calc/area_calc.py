# -*- coding: utf-8 -*-

#Open shapefile in zip
#Add field with area


from osgeo import ogr, osr
import os

ogr.UseExceptions()

def calc_area():

        
        area_fieldname = 'Area'

        filename = r"c:\temp\zones2.shp"
        filename_output = r"c:\temp\zones3.shp"
        overwrite = True
        
        #os.environ['SHAPE_ENCODING'] = "utf-8"
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(filename,1)
        layer = dataSource.GetLayer()



        
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
        
        

        #reproject area from his CRS to UTM
        source = layer.GetSpatialRef()

        target = osr.SpatialReference()
        target.ImportFromEPSG(epsg_utm)

        transform = osr.CoordinateTransformation(source, target)
        
        #create output layer
        driver_output = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(filename_output):
            if overwrite:
                driver_output.DeleteDataSource(filename_output)
            else:
                raise IOError("file already exists")

        outdatasource = driver_output.CreateDataSource(filename_output)
        layername = layer.GetName()
        #print layername
        #quit()
        outlayer = outdatasource.CreateLayer('outlayer', geom_type=ogr.wkbMultiPolygon, options=['ENCODING=UTF-8'])
        
        outlayerdef = outlayer.GetLayerDefn()

        srclayerDefinition = layer.GetLayerDefn()
        for i in range(srclayerDefinition.GetFieldCount()):
            outlayer.CreateField(srclayerDefinition.GetFieldDefn(i))
        
        
        #add field for area
        field_defenition = ogr.FieldDefn(area_fieldname,ogr.OFTString)
        outlayer.CreateField(field_defenition)
        
        #walk by layer1 features
        layer.ResetReading()
        feature = layer.GetNextFeature()
        while feature:
            
            geom_feature = feature.GetGeometryRef()
            geom_feature.Transform(transform)
            #calculate 
            total_area = geom_feature.GetArea()
            
            outFeature = ogr.Feature(outlayerdef)
            outFeature.SetGeometry(feature.GetGeometryRef())
            

            #for j in range( srclayerDefinition.GetFieldCount()):
            #    outFeature.SetField(srclayerDefinition.GetFieldDefn(j).GetName(), feature.GetField(j))
            outFeature.SetFrom(feature)
                
            #write calc result to attribute
            outFeature.SetField(area_fieldname,str(total_area))
            #feature.SetGeometry(feature.GetGeometryRef())
            if outlayer.CreateFeature(outFeature) != 0:
                print 'outlayer.CreateFeature failed'
                
            
            feature = layer.GetNextFeature()
        layer.ResetReading()
        dataSource.Destroy()
        outdatasource = None


calc_area()