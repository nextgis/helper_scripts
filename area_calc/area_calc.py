# -*- coding: utf-8 -*-

#Open shapefile in zip
#Add field with area


from osgeo import ogr, osr, gdal
import os
import tempfile,shutil,zipfile
from geographiclib.geodesic import Geodesic
from progress.bar import Bar

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
        calc_area_shp(source_filename,output_filename,mode='utm')
    elif source_filename.lower().endswith('.zip'):
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

def get_utm_zone_by_point(point,source_crs):
        target_crs = osr.SpatialReference()
        target_crs.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(source_crs, target_crs)
        point.Transform(transform)
        #Get number of UTM zone for point using magic numbers
        x = int(point.GetX() // 6)
        zone = x + 31
        epsg_utm = zone + 32600
        if int(point.GetX()) < 0 :
            epsg_utm = zone + 32700 #south hemisphere

        return epsg_utm

def calc_area_shp(source_filename, output_filename, mode = 'geodesics'):

        area_fieldname = 'Area'

        #filename = r"c:\temp\zones2.shp"
        #filename_output = r"c:\temp\zones3.shp"
        filename = source_filename
        filename_output = output_filename
        overwrite = True

        #os.environ['SHAPE_ENCODING'] = "utf-8"
        driver = ogr.GetDriverByName("ESRI Shapefile")
        #dataSource = driver.Open(filename,1) #,open_options=['ENCODING=UTF-8']
        dataSource = gdal.OpenEx(filename,gdal.OF_VECTOR | gdal.OF_UPDATE,open_options=['ENCODING=UTF-8']) #,
        layer = dataSource.GetLayer()

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

        #copy fields definitions to new layer
        srclayerDefinition = layer.GetLayerDefn()
        for i in range(srclayerDefinition.GetFieldCount()):
            outlayer.CreateField(srclayerDefinition.GetFieldDefn(i))

        #add new real field for area
        field_defenition = ogr.FieldDefn(area_fieldname,ogr.OFTReal)
        field_defenition.SetWidth(20)
        field_defenition.SetPrecision(3)
        outlayer.CreateField(field_defenition)


        #calculate count of footprints for progressbar
        keys_count = 0
        feature = layer.GetNextFeature()
        while feature:
                 keys_count = keys_count + 1
                 feature = layer.GetNextFeature()
        layer.ResetReading()

        #walk by source layer features
        source_crs = layer.GetSpatialRef()
        layer.ResetReading()
        feature = layer.GetNextFeature()
        bar = Bar('Calculate areas', max=keys_count, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
        while feature:
            bar.next()

            #copy feature to new layer
            outFeature = ogr.Feature(outlayerdef)
            outFeature.SetFrom(feature)

            if mode == 'utm':
                #reproject area from his CRS to UTM
                geom_feature = feature.GetGeometryRef()
                epsg_utm = get_utm_zone_by_point(geom_feature.Centroid(),source_crs)
                target_crs = osr.SpatialReference()
                target_crs.ImportFromEPSG(epsg_utm)
                transform = osr.CoordinateTransformation(source_crs, target_crs)
                geom_feature.Transform(transform)

                #calculate
                total_area = geom_feature.GetArea()
            elif mode == 'geodesics':
                #reproject area from his CRS to 4326
                geom_feature = feature.GetGeometryRef()
                target_crs = osr.SpatialReference()
                target_crs.ImportFromEPSG(4326)
                transform = osr.CoordinateTransformation(source_crs, target_crs)
                geom_feature.Transform(transform)

                ring = geom_feature.GetGeometryRef(0)
                geod = Geodesic.WGS84
                geod_polygon = geod.Polygon()
                for p in xrange(ring.GetPointCount()):
                    lon, lat, z = ring.GetPoint(p)
                    #print '{lon} - {lat}'.format(lon=lon,lat=lat)
                    geod_polygon.AddPoint(lon,lat)

                num, perim, total_area = geod_polygon.Compute()
                pack = geod_polygon.Compute()
                print pack

            #write calc result to attribute
            outFeature.SetField(area_fieldname,str(total_area))
            if outlayer.CreateFeature(outFeature) != 0:
                print 'outlayer.CreateFeature failed'


            feature = layer.GetNextFeature()
        layer.ResetReading()
        bar.finish()
        dataSource = None
        outdatasource = None

if __name__ == "__main__":
    parser = argparser_prepare()
    args = parser.parse_args()
    detect_filetype(args.source_filename[0], args.output_filename[0]) #argparse unnamed args return as list
