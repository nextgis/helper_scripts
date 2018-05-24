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

if platform.uname()[0] == 'Windows':
    path = 'c:/tools/7-Zip/'
else:
    path = ''

#os.chdir('all')
files = glob.glob('*.7z')
output = open('result.csv','wb')
output.write('ID;REG;LAYER;NUM\n')

for f in files:
    f_reg = f.split('-2018')[0]
    print('Processing ' + f)
    
    
    #unpack
    cmd = path + '7z x -otemp ' + f + ' > nul'
    os.system(cmd)
    if os.path.exists('nul'): os.remove('nul')
    os.chdir('temp/data')
    
    #calculate
    list_of_layers = glob.glob('*.shp')
    for layer_shp in list_of_layers:
        layer = layer_shp.replace('.shp','')
        cmd = 'ogrinfo -so %s %s | grep Feature > tmp' % (layer_shp,layer)
        os.system(cmd)
        res = open('tmp', 'r').readline().replace('Feature Count: ','')
        
        output.write(f_reg + ';' + layer + ';' + res)
        
        
    #cleanup
    os.chdir('../../')
    shutil.rmtree('temp')
    
output.close()