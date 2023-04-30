# -*- coding: utf-8 -*-
#get number of features for latest 7z for each subfolder in a folder
#run 
#sudo -u postgres psql -d osmshp -t -A -F";" -c "SELECT id, code FROM region" > regs.csv
#then move results.csv to data.nextgis.com

import os
import glob
import shutil
import csv
import platform
from osgeo import ogr

if platform.uname()[0] == 'Windows':
    zippath = 'c:/tools/'
else:
    zippath = ''

cur_dir = os.getcwd()
dst_dir = 'd:/Programming/Python/helper_scripts/get_number_of_features/'
data_dir = dst_dir + '/data/' 

os.chdir(data_dir)
files = glob.glob('*.zip')
files.sort()
os.chdir(dst_dir)

ext = 'gpkg'
#ext = 'shp'
driver_str = 'GPKG'
#driver_str = 'ESRI Shapefile'
format = 'gpkg'
#format = 'shape'

output = open('result.csv','w')
#output.write('REG;LAYER;NUM\n')

for f in files:
    f_reg = f.replace('-%s.zip' % format,'')
    print('Processing ' + f)
    
    if os.path.getsize(data_dir + f) > 22:

        #unpack
        shutil.copy(data_dir + f,dst_dir)
        os.chdir(cur_dir)
        cmd = zippath + 'unzip -q ' + f + ' -d temp'
        os.system(cmd)
        #if os.path.exists('nul'): os.remove('nul')
        os.chdir('temp')
        
        #calculate
        #list_of_layers = glob.glob('data\*.' + ext)
        list_of_layers = glob.glob('*.' + ext)
        for layer in list_of_layers:
            if '-lvl' not in layer:
                layer_name = layer.replace('.' + ext,'')
                driver = ogr.GetDriverByName(driver_str)
                source_ds = driver.Open(layer, 0)
                layer = source_ds.GetLayerByIndex(0)
                res = layer.GetFeatureCount()
                
                output.write(f_reg + ';' + layer_name + ';' + str(res) + '\n')
                source_ds.Destroy()

        #cleanup
        os.chdir('..')
        shutil.rmtree('temp')
        os.remove(f)

output.close()