#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import argparse

def get_args():
    epilog = '''
    Example:
    /media/trolleway/46fa49bc-b42a-411f-99f6-4a24dbea79dd/home/trolleway/GIS/project161_fires/process/helper_scripts/imagery_download$ ./batch_reproject.py /media/trolleway/46fa49bc-b42a-411f-99f6-4a24dbea79dd/home/trolleway/GIS/project161_fires/201911/test /media/trolleway/46fa49bc-b42a-411f-99f6-4a24dbea79dd/home/trolleway/GIS/project161_fires/201911/test/3857
    



    '''
    p = argparse.ArgumentParser(description='Batch reproject rasters files. Batch wrapper of gdalwarp -t_srs EPSG:3857 ', epilog = epilog)
    p.add_argument('--t_srs', required=False, default='EPSG:3857', help='EPSG code of projection', type=str)
    p.add_argument('path', help='source folder', type=str)
    p.add_argument('dest', help='target folder', type=str)
    
    return p.parse_args()



'''


'''



if __name__ == '__main__':

    args = get_args()
    path = args.path
    dest = args.dest
    t_srs = args.t_srs

    fnames = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    tiffs = list()
    for f in fnames:
        if f.lower().endswith(".tif") or f.lower().endswith(".tiff"):
            tiffs.append(f)

    for filename in tiffs:
        src = os.path.join(path,filename)
        tiff_dest = os.path.join(dest,os.path.basename(filename))
        #print dest
        #quit()
        t_srs = args.t_srs
        cmd = 'gdalwarp -overwrite -t_srs {t_srs} {src} {dest}'
        cmd = cmd.format(t_srs = t_srs, src=src, dest=tiff_dest)
        print
        print cmd
        os.system(cmd)