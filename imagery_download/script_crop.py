'''
virtualenv venv
source venv/bin/activate

pip install -U pip
pip install rio-color

'''
import os
import tempfile

scenes = list()
scenes.append({'id': '2019-1','event_date':'2019-03-22','date':'20190409' ,'imagery':'/home/trolleway/ssdgis/161_fires/landsat-work/LC08_L1TP_125025_20190409_20190422_01_T1/LC08_L1TP_125025_20190409_20190422_01_T1_pan.tif'})
scenes.append({'id': '2019-2','event_date':'2019-04-11','date':'20190416' ,'imagery':'/home/trolleway/ssdgis/161_fires/landsat-work/LC08_L1TP_126025_20190416_20190423_01_T1/LC08_L1TP_126025_20190416_20190423_01_T1_pan.tif'})
scenes.append({'id': '2019-3s', 'event_date':'2019-04-15','date':'20190506' ,'imagery':'/home/trolleway/ssdgis/161_fires/sentinel-manual/S2B_MSIL2A_20190506T031549_N0212_R118_T50ULA_20190521T162112.tif'})
scenes.append({'id': '2019-3t', 'event_date':'2019-04-15','date':'20190416' ,'imagery':'/home/trolleway/ssdgis/161_fires/landsat-work/LC08_L1TP_126025_20190416_20190423_01_T1/LC08_L1TP_126025_20190416_20190423_01_T1_pan.tif'})
scenes.append({'id': '2019-4', 'event_date':'2019-04-19','date':'20190506' ,'imagery':'/home/trolleway/ssdgis/161_fires/sentinel-manual/S2B_MSIL2A_20190506T031549_N0212_R118_T50ULA_20190521T162112.tif'})
scenes.append({'id': '2019-5', 'event_date':'2019-04-20','date':'20190425' ,'imagery':'/home/trolleway/ssdgis/161_fires/landsat-work/LC08_L1TP_125025_20190425_20190508_01_T1/LC08_L1TP_125025_20190425_20190508_01_T1_pan.tif'})
scenes.append({'id': '2019-6', 'event_date':'2019-04-20','date':'20190502' ,'imagery':'/home/trolleway/ssdgis/161_fires/landsat-work/LC08_L1TP_126025_20190502_20190508_01_T1/LC08_L1TP_126025_20190502_20190508_01_T1_pan.tif'})

scenes.append({'id': '2019-1','event_date':'2019-03-22','date':'20190305' ,'imagery':'/home/trolleway/ssdgis/161_fires/sentinel/S2A_MSIL2A_20190305T032621_N0211_R018_T50UMA_20190305T073635.tif'})
scenes.append({'id': '2019-2','event_date':'2019-04-11','date':'20190416' ,'imagery':''})
scenes.append({'id': '2019-3s', 'event_date':'2019-04-15','date':'20190409' ,'imagery':'/home/trolleway/ssdgis/161_fires/sentinel/S2B_MSIL2A_20190409T032539_N0211_R018_T50ULA_20190409T073542.tif'})
scenes.append({'id': '2019-3t', 'event_date':'2019-04-15','date':'20190409' ,'imagery':'/home/trolleway/ssdgis/161_fires/sentinel/S2B_MSIL2A_20190409T032539_N0211_R018_T50ULA_20190409T073542.tif'})
scenes.append({'id': '2019-4', 'event_date':'2019-04-19','date':'20190409' ,'imagery':'/home/trolleway/ssdgis/161_fires/sentinel/S2B_MSIL2A_20190409T032539_N0211_R018_T50ULA_20190409T073542.tif'})
scenes.append({'id': '2019-5', 'event_date':'2019-04-20','date':'20190409' ,'imagery':'/home/trolleway/ssdgis/161_fires/landsat-work/LC08_L1TP_125025_20190409_20190422_01_T1/LC08_L1TP_125025_20190409_20190422_01_T1_pan.tif'})
scenes.append({'id': '2019-6', 'event_date':'2019-04-20','date':'20190421' ,'imagery':'/home/trolleway/ssdgis/161_fires/sentinel-manual/T50UMB_20190421T031541_mul_lzw.tif'})





for scene in scenes:

    source = '/home/trolleway/ssdgis/161_fires/fires2019/fires2019_v2.shp'
    temp_feature_fileobj1 = tempfile.NamedTemporaryFile(suffix='.gpkg')
    temp_feature_file1 = temp_feature_fileobj1.name
    temp_feature_fileobj2 = tempfile.NamedTemporaryFile(suffix='.gpkg')
    temp_feature_file2 = temp_feature_fileobj2.name

    temp_raster_fileobj = tempfile.NamedTemporaryFile(suffix='.tif')
    temp_raster = temp_raster_fileobj.name
    temp_raster_fileobj2 = tempfile.NamedTemporaryFile(suffix='.tif')
    temp_raster2 = temp_raster_fileobj2.name


    os.unlink(temp_feature_file1)
    os.unlink(temp_feature_file2)
    cmd = '''ogr2ogr -overwrite -t_srs EPSG:32650 -where "id_txt='{id}'" {feature_file} {source}'''
    cmd = cmd.format(source=source,feature_file=temp_feature_file1,date=scene['date'],id=scene['id'])
    print cmd
    os.system(cmd)


    buffer_meters = 3000
    cmd = '''ogr2ogr -overwrite -t_srs EPSG:32650 -dialect SQLite -sql " SELECT ST_Buffer(geom, {buffer_meters}) FROM fires2019_v2 ''' + '"' + '''   {feature_file2} {feature_file} '''
    cmd = cmd.format(feature_file=temp_feature_file1,feature_file2=temp_feature_file2,buffer_meters=str(buffer_meters))
    print cmd
    os.system(cmd)
    print

    cmd = 'gdalwarp -dstalpha -overwrite -co COMPRESS=LZW -cutline {cutlinepath} -crop_to_cutline {imagery} {dest}'
    cmd = cmd.format(cutlinepath=temp_feature_file2,feature_file2=temp_feature_file2,imagery=scene['imagery'],dest = temp_raster)
    print cmd
    os.system(cmd)
    print


    cmd = 'rio color {src} {dest} sigmoidal rgb 10 0.5 '
    cmd = cmd.format(src = temp_raster, dest=temp_raster2)
    print cmd
    os.system(cmd)
    print

    #cmd = 'gdal_translate  {src} {dest}'
    # -histeq 32768
    cmd = 'gdal_contrast_stretch  -percentile-range 0.02 0.98 {src} {dest}'
    cmd = cmd.format(src = temp_raster2, dest = scene['id']+'_pozar'+scene['event_date']+'_'+scene['date']+'.tif')
    print cmd
    os.system(cmd)
