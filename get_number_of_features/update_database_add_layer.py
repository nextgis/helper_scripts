# -*- coding: utf-8 -*-
#update database with numbers of features
#run 
#get_number_of_features.py
#before running this script
#Execute: UPDATE layer_version SET row_count_alt = 911 WHERE layer_id = 'surface-polygon' AND region_id = 37;
#on data.nextgis.com

import os
import csv

with open('result.csv', 'rb') as f:
    reader = csv.reader(f,delimiter=';')
    items = list(reader)

for i in items[1:]:
    if i[2] == 'aerialway-point' or i[2] == 'aerialway-line' or i[2] == 'public-transport-point' or i[2] == 'parking-polygon' or i[2] == 'highway-crossing-point':
        print('Processing ' + i[1])
        cmd = 'sudo -u postgres psql -d osmshp -t -A -F";" -c "INSERT INTO layer_version (region_id, layer_id, ts, row_count, row_count_alt) VALUES (%s, \'%s\', \'2016-11-13 00:00:00\', 0, %s);"' % (i[0],i[2],i[3])
        os.system(cmd)
    
    
    