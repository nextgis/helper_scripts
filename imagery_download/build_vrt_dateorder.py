#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import argparse

def get_args():
    epilog = '''
    Имеется пачка с 100 сценами Sentinel
Скрипт генерирует для каждого файл vrt названый по дате, так что бы кинуть их в qgis, 
и они отсортировались по дате, а не по названию аппарата.

vrt не поддерживает объединение растров в разных сисемах координат, поэтому пердварительно перепроецируйте свои растры в EPSG:3857

folder='*'
mkdir $folder/3857
for f in $folder ; do;  echo gdalwarp  -t_srs EPSG:3857 $f $folder/3857/$f ; done



    '''
    p = argparse.ArgumentParser(description='make vrt files for Sentinel2 scenes, ordered by date', epilog = epilog)
    p.add_argument('path', help='path', type=str)
    
    return p.parse_args()



'''


'''

def extract_date_from_filename(filename):
    start = 11
    datetext = filename[start:start+8]
    return datetext


def build_vrt_by_dates(path):

    scenes=dict()
    scenes['platform2']=list()
    lists_by_dates = dict()

    #get list of files
    tiffs = list()
    for dirpath, dnames, fnames in os.walk(path):
        for f in fnames:
            if f.lower().endswith(".tif") or f.lower().endswith(".tiff"):
                tiffs.append(f)


    #determine product by filename
    for tiff in tiffs:
        platform = 'sentinel2'
        if platform == 'sentinel2':
            scenes['platform2'].append(tiff)
    
    #builid text list
    for scene in scenes['platform2']:
        datetext = extract_date_from_filename(scene)

        if datetext not in lists_by_dates:
            lists_by_dates[datetext]=list()
        
        lists_by_dates[datetext].append(scene)


    #call gdalbuildvrt with text list
    for date in lists_by_dates:
        #folder = get_folder_from_path(path)
        list_filename = os.path.join(path,'list.txt')
        vrts_folder = os.path.join(path,'vrts')
        if not os.path.exists(vrts_folder):
            os.makedirs(vrts_folder)

        vrt_filename = str(date) +' Sentinel2'+'.vrt'
        vrt_filename = os.path.join(path,vrt_filename)



 
        with open(list_filename, 'w') as f:
            for item in lists_by_dates[date]:
                f.write("%s\n" % os.path.join(path,item))

        
        cmd = 'gdalbuildvrt -input_file_list {list_filename} -allow_projection_difference "{vrt_filename}" '
        cmd = cmd.format(list_filename = list_filename, vrt_filename = vrt_filename)
        
        os.system(cmd)

        

if __name__ == '__main__':

    args = get_args()

    build_vrt_by_dates(args.path)