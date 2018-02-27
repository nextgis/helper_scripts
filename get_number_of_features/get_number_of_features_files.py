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

path = 'c:/tools/7-Zip/'

with open('regs.csv', 'rb') as f:
    reader = csv.reader(f)
    regs = list(reader)

os.chdir('all')
files = glob.glob('*.7z')
output = open('result.csv','wb')
output.write('ID;REG;LAYER;NUM\n')

for f in files:
    f_reg = f.split('-18')[0]
    reg = [x for x in regs if f_reg == x[1]]
    if len(reg) == 1:
        print('Processing ' + f)
        
        #get reg id
        reg_id = reg[0][0]
        
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
            
            output.write(reg_id + ';' + f_reg + ';' + layer + ';' + res)
            
            
        #cleanup
        os.chdir('../../')
        shutil.rmtree('temp')
    
output.close()