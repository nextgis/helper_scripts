# -*- coding: utf-8 -*-
#get number of features for latest 7z for each subfolder in a folder
#run 
#sudo -u postgres psql -d osmshp -t -A -F";" -c "SELECT id, code FROM region" > regs.csv
#then move results.csv to data.nextgis.com

import os,argparse
import glob
import shutil
import platform
from osgeo import ogr

parser = argparse.ArgumentParser()
parser.add_argument('-p','--product', required=False, choices=['osm','msbld','reforma','dem', 'oopt', 'rnlic'], help='Unzip first')
args = parser.parse_args()
if not args.product: product = ''

if platform.uname()[0] == 'Windows':
    zippath = 'c:/tools/7-Zip/'
else:
    zippath = ''

cur_dir = os.getcwd()
dst_dir = os.getcwd()
data_dir = os.path.join(dst_dir,'data')

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

for f in files:
    full_path = os.path.join(data_dir,f)
    f_reg = f.replace('.zip','').replace('-%s.zip' % format,'')
    print('Processing ' + f)
    
    if os.path.getsize(full_path) > 22:

        #unpack
        shutil.copy(full_path,dst_dir)
        os.chdir(cur_dir)
        cmd = zippath + '7z x ' + f + ' -otemp'
        os.system(cmd)
        os.chdir('temp')
        
        #calculate
        if os.path.exists('data'):
            list_of_layers = glob.glob('data\*.' + ext)
        else:
            list_of_layers = glob.glob('*.' + ext)
            
        for layer in list_of_layers:
            if '-lvl' not in layer:
                layer_name = layer.replace('.' + ext,'').replace('data\\','')
                driver = ogr.GetDriverByName(driver_str)
                source_ds = driver.Open(layer, 0)
                layer = source_ds.GetLayerByIndex(0)
                res = layer.GetFeatureCount()
                
                output.write(f_reg + ';' + layer_name + ';' + str(res) + ';' + product + '\n')
                source_ds.Destroy()

        #cleanup
        os.chdir('..')
        shutil.rmtree('temp')
        os.remove(f)

output.close()