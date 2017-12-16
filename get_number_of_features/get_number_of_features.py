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

cwd = os.getcwd()
dirs = next(os.walk(cwd))[1]
dirs.remove('latest')
output = open('result.csv','wb')
output.write('reg;layer;num\n')

with open('regs.csv', 'rb') as f:
    reader = csv.reader(f)
    regs = list(reader)

for dir in dirs:
    #check if dir is in list of regions
    reg = [x for x in regs if dir == x[1]]
    if len(reg) == 1:
        #go into dir
        os.chdir(dir)
        print('Processing ' + dir)
        
        #find the freshest archive
        list_of_files = glob.glob('*')
        latest_file = max(list_of_files, key=os.path.getctime)
        
        #get reg id
        reg_id = reg[0][0]
        
        #unpack
        cmd = '7z x -otemp ' + latest_file + ' > nul'
        #if os.path.exists('nul'): os.remove('nul')
        os.system(cmd)
        os.remove('nul')
        os.chdir('temp/data')
        
        #calculate
        list_of_layers = glob.glob('*.shp')
        for layer_shp in list_of_layers:
            layer = layer_shp.replace('.shp','')
            cmd = 'ogrinfo -so %s %s | grep Feature > tmp' % (layer_shp,layer)
            os.system(cmd)
            res = open('tmp', 'r').readline().replace('Feature Count: ','')
            
            output.write(reg_id + ';' + dir + ';' + layer + ';' + res)
            
            
        #cleanup
        os.chdir('../../')
        shutil.rmtree('temp')
        
        #return
        os.chdir(cwd)
    
output.close()