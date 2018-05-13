#if there geom differences - send new geom to QMS
import getpass
import os
import csv

pwd = getpass.getpass()

f_csv = "list.csv"
with open(f_csv, 'rb') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=';')

    for row in csvreader:
        if 'geom' in row['changes_sync']:
            qms_id = row['qms_id']
            wkt = row['osmlab_wkt']
            if len(wkt)<1000:
                cmd = 'c:\python27\python update_bbox.py --user admin_qms --passw %s --sid %s --bstr "SRID=4326;%s"' % (pwd,qms_id,wkt)
            else:
                with open('temp.wkt','wb') as f_wkt:
                    f_wkt.write(wkt)
                cmd = 'c:\python27\python update_bbox.py --user admin_qms --passw %s --sid %s --bfile temp.wkt' % (pwd,qms_id)
            print('Updating ' + row['name'])
            #print(cmd)
            os.system(cmd)
            
if os.path.exists('temp.wkt'): os.remove('temp.wkt')