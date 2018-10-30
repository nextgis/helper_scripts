# -*- coding: utf-8 -*-

#Open shapefile in zip
#Add field with area


import os
import tempfile, shutil, zipfile


from osgeo import ogr, osr, gdal



ogr.UseExceptions()

import argparse


def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 45

    parser = argparse.ArgumentParser(description='''Script open zip with shapefile. Replace zip file with new with shp with zipname field.''',
            formatter_class=PrettyFormatter)
    parser.add_argument('source_filename', nargs=1)
    parser.add_argument('--fieldname',default='Name')


    parser.epilog = \
        '''Samples:
python %(prog)s ../2346.zip
python %(prog)s --fieldname Ref ../2346.zip
      For each zip in folder:
find ~/tmp/folder_with_zips/ -name "*.zip" -exec "python %(prog)s --fieldname Ref {}" \;
for f in ~/tmp/folder_with_zips/*.zip; do python zipname2attr.py --fieldname Ref $f ; done
''' \
        % {'prog': parser.prog}
    return parser


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def main(source_filename,fieldname):
    if source_filename.lower().endswith('.zip'):
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

        source_shp_filepath = os.path.join(temporary_folder, source_shp_filename)
        output_shp_filepath = os.path.join(temporary_folder_output, source_shp_filename)

        zipname = os.path.splitext(os.path.basename(source_filename))[0]

        add_field_shp(source_shp_filepath, output_shp_filepath,fieldname=fieldname, fieldvalue=zipname)

        archive_filepath = os.path.join(temporary_folder_zip,os.path.basename(source_filename)) + '.zip'
        archive_filepath = os.path.join(temporary_folder_zip,os.path.splitext(os.path.basename(source_filename))[0]) + '2'

        shutil.make_archive(archive_filepath, 'zip', temporary_folder_output)

        shutil.move(archive_filepath+'.zip',source_filename)

        shutil.rmtree(temporary_folder)
        shutil.rmtree(temporary_folder_output)
        shutil.rmtree(temporary_folder_zip)
    else:
        raise ValueError('Input file should be .shp or .zip')
        sys.exit(1)


def add_field_shp(source_filename, output_filename, fieldname, fieldvalue):

        filename = source_filename
        filename_output = output_filename
        overwrite = True

        #os.environ['SHAPE_ENCODING'] = "utf-8"
        driver = ogr.GetDriverByName("ESRI Shapefile")
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

        outlayer = outdatasource.CreateLayer('outlayer', layer.GetSpatialRef(), geom_type=layer.GetGeomType(), options=['ENCODING=UTF-8'])
        outlayerdef = outlayer.GetLayerDefn()

        #copy fields definitions to new layer
        srclayerDefinition = layer.GetLayerDefn()
        for i in range(srclayerDefinition.GetFieldCount()):
            outlayer.CreateField(srclayerDefinition.GetFieldDefn(i))

        #add new real field for area
        field_defenition = ogr.FieldDefn(fieldname, ogr.OFTString)
        field_defenition.SetWidth(250)
        field_defenition.SetPrecision(4)
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
        #bar = Bar('Add field', max=keys_count, suffix='%(index)d/%(max)d - %(percent).1f%% - %(eta)ds')
        while feature:
            #bar.next()

            #copy feature to new layer
            outFeature = ogr.Feature(outlayerdef)
            outFeature.SetFrom(feature)

            #write calc result to attribute
            outFeature.SetField(fieldname, fieldvalue)
            if outlayer.CreateFeature(outFeature) != 0:
                print 'outlayer.CreateFeature failed'

            feature = layer.GetNextFeature()
        layer.ResetReading()
        #bar.finish()
        dataSource = None
        outdatasource = None

if __name__ == "__main__":
    parser = argparser_prepare()
    args = parser.parse_args()
    main(args.source_filename[0], args.fieldname)
