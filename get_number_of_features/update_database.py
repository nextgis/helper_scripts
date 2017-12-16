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
    print('Processing ' + i[1])
    cmd = 'sudo -u postgres psql -d osmshp -t -A -F";" -c "UPDATE layer_version SET row_count_alt = %s WHERE layer_id = \'%s\' AND region_id = %s;"' % (i[3],i[2],i[0])
    os.system(cmd)