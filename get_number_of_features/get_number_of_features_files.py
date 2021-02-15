# -*- coding: utf-8 -*-
#get number of features for latest 7z for each subfolder in a folder
#run 
#sudo -u postgres psql -d osmshp -t -A -F";" -c "SELECT id, code FROM region" > regs.csv
#on pluk before running this script
#then move results.csv to data.nextgis.com

import os
import glob
import shutil
import csv
import platform
from osgeo import ogr

if platform.uname()[0] == 'Windows':
    path = 'c:/tools/7-Zip/'
else:
    path = ''

cur_dir = os.getcwd()
data_dir = '//nextgis-nas/share/data/'
dst_dir = 'd:/Programming/Python/helper_scripts/get_number_of_features/'


os.chdir(data_dir)
files = glob.glob('*.zip')
os.chdir(dst_dir)

output = open('result.csv','w')
output.write('REG;LAYER;NUM\n')

for f in files:
    f_reg = f.split('-')[0] + '-' + f.split('-')[1]
    print('Processing ' + f)
        
    #unpack
    shutil.copy(data_dir + f,dst_dir)
    os.chdir(cur_dir)
    cmd = path + '7z x -otemp ' + f + ' >nul'
    os.system(cmd)
    #if os.path.exists('nul'): os.remove('nul')
    os.chdir('temp/data')
    
    #calculate
    list_of_layers = glob.glob('*.shp')
    for layer_shp in list_of_layers:
        layer_name = layer_shp.replace('.shp','')
        driver = ogr.GetDriverByName("ESRI Shapefile")
        source_ds = driver.Open(layer_shp, 0)
        layer = source_ds.GetLayerByIndex(0)
        res = layer.GetFeatureCount()
        
        output.write(f_reg + ';' + layer_name + ';' + str(res) + '\n')

        source_ds.Destroy()

    list_of_layers = glob.glob('*.gpkg')
    for layer_gpkg in list_of_layers:
        layer_name = layer_gpkg.replace('.gpkg','')
        driver = ogr.GetDriverByName("GPKG")
        source_ds = driver.Open(layer_gpkg, 0)
        layer = source_ds.GetLayerByIndex(0)
        res = layer.GetFeatureCount()
        
        output.write(f_reg + ';' + layer_name + ';' + str(res) + '\n')

        source_ds.Destroy()

    #cleanup
    os.chdir('../../')
    shutil.rmtree('temp')
    os.remove(f)

output.close()