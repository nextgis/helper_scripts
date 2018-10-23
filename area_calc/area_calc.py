# -*- coding: utf-8 -*-

#Open shapefile in zip
#Add field with area


from osgeo import ogr, osr
import os
import tempfile,shutil,zipfile

ogr.UseExceptions()

import argparse
def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 45

    parser = argparse.ArgumentParser(description='''Script open ESRI Shapefile or zip with shapefile. Replace zip file with new with shp with added area field. \n Area calculated in UTM with meters''',
            formatter_class=PrettyFormatter)
    parser.add_argument('source_filename', nargs=1)
    parser.add_argument('output_filename', nargs='?',default='None')

    parser.epilog = \
        '''Samples: 
#upload all geojsons and geotiff from current folder
time python %(prog)s ../source.shp ../output.shp
''' \
        % {'prog': parser.prog}
    return parser
    
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

            
def detect_filetype(source_filename, output_filename=''):
    if source_filename.lower().endswith('.shp'):
        if output_filename == '' or output_filename == 'None':
            raise ValueError('Output name should be not null for work with shp')
            sys.exit(1)            
        calc_area_shp(source_filename,output_filename)
    elif source_filename.lower().endswith('.zip'):
        print 'zip'
        temporary_folder = tempfile.mkdtemp()
        temporary_folder_output = tempfile.mkdtemp()
        temporary_folder_zip = tempfile.mkdtemp()
        
        #unzip
        zip_ref = zipfile.ZipFile(source_filename, 'r')
        zip_ref.extractall(temporary_folder)
        zip_ref.close()
        
        #search shapefile in folder 
        source_shp_filename = None
        for file in os.listdir(temporary_folder):
            if file.lower().endswith(".shp"):
                source_shp_filename = file
                break
        if source_shp_filename is None:
            raise ValueError('zip unpacked, but no .shp file found')
            sys.exit(1)
    
        source_shp_filepath = os.path.join(temporary_folder,source_shp_filename)
        output_shp_filepath = os.path.join(temporary_folder_output,source_shp_filename)
        
        calc_area_shp(source_shp_filepath, output_shp_filepath)
        
        archive_filepath = os.path.join(temporary_folder_zip,os.path.basename(source_filename))+'.zip'
        archive_filepath = os.path.join(temporary_folder_zip,os.path.splitext(os.path.basename(source_filename))[0])+'2'
        #print archive_filepath
        #print os.path.basename(source_shp_filename)
        
        #zipf = zipfile.ZipFile(archive_filepath, 'w', zipfile.ZIP_DEFLATED)
        #zipdir(temporary_folder_output, zipf)
        #zipf.close()
        
        shutil.make_archive(archive_filepath, 'zip', temporary_folder_output)
        #print os.path.isfile(archive_filepath+'.zip')
        
        #pack(temporary_shp,temporary_zip)
        shutil.move(archive_filepath+'.zip',source_filename)

        #replace(temporary_zip,source_zip)
        shutil.rmtree(temporary_folder)
        shutil.rmtree(temporary_folder_output)
        shutil.rmtree(temporary_folder_zip)
    else:
        raise ValueError('Input file should be .shp or .zip')
        sys.exit(1)
def calc_area_shp(source_filename, output_filename):

        
        area_fieldname = 'Area'

        #filename = r"c:\temp\zones2.shp"
        #filename_output = r"c:\temp\zones3.shp"
        filename = source_filename
        filename_output = output_filename
        overwrite = True
        
        #os.environ['SHAPE_ENCODING'] = "utf-8"
        driver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = driver.Open(filename,1)
        layer = dataSource.GetLayer()



        
        frist_feature = layer.GetNextFeature()
        geometry = frist_feature.GetGeometryRef()
        layer.ResetReading()


        #reproject layers  to utm for area calc

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


        outlayer = outdatasource.CreateLayer('outlayer', layer.GetSpatialRef(), geom_type=ogr.wkbMultiPolygon, options=['ENCODING=UTF-8'])
        
        outlayerdef = outlayer.GetLayerDefn()

        srclayerDefinition = layer.GetLayerDefn()
        for i in range(srclayerDefinition.GetFieldCount()):
            outlayer.CreateField(srclayerDefinition.GetFieldDefn(i))
        
        
        #add field for area
        field_defenition = ogr.FieldDefn(area_fieldname,ogr.OFTReal)
        field_defenition.SetWidth(20)
        field_defenition.SetPrecision(3)
        outlayer.CreateField(field_defenition)
        
        #walk by layer1 features
        layer.ResetReading()
        feature = layer.GetNextFeature()
        while feature:
            
            outFeature = ogr.Feature(outlayerdef)
            outFeature.SetFrom(feature)
            
            #geometry = feature.GetGeometryRef()
            #geometry = ogr.ForceToMultiPolygon(geometry)
            #outFeature.SetGeometry(geometry)
            #del geometry 
            geom_feature = feature.GetGeometryRef()
            geom_feature.Transform(transform)
            #calculate 
            total_area = geom_feature.GetArea()
            
            

            #for j in range( srclayerDefinition.GetFieldCount()):
            #    outFeature.SetField(srclayerDefinition.GetFieldDefn(j).GetName(), feature.GetField(j))
                
            
            #write calc result to attribute
            outFeature.SetField(area_fieldname,str(total_area))
            if outlayer.CreateFeature(outFeature) != 0:
                print 'outlayer.CreateFeature failed'
                
            
            feature = layer.GetNextFeature()
        layer.ResetReading()
        dataSource.Destroy()
        outdatasource = None

if __name__ == "__main__":
    parser = argparser_prepare()
    args = parser.parse_args()
    detect_filetype(args.source_filename[0], args.output_filename[0]) #argparse unnamed args return as list