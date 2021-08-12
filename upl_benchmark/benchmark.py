#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ogr, osr
import os
import math
import shutil
import time
import csv
import datetime
from alive_progress import alive_bar

import pyngw
#pip3 install --upgrade --force-reinstall git+https://github.com/nextgis/pyngw.git

ngw_url = 'https://sandbox.nextgis.com'
login = 'administrator'
password = 'demodemo'
GROUP = 0




DIR = 'DUMPS'
if os.path.exists(DIR) and os.path.isdir(DIR):
    shutil.rmtree(DIR)
os.mkdir(DIR)

DATADIR = 'LAYER'
if os.path.exists(DATADIR) and os.path.isdir(DATADIR):
    shutil.rmtree(DATADIR)
os.mkdir(DATADIR)

STATISTICDIR = 'STATISTICS'
if not os.path.exists(STATISTICDIR) and not os.path.isdir(STATISTICDIR):
    os.mkdir(STATISTICDIR)


ngwapi = pyngw.Pyngw(ngw_url = ngw_url, login = login, password = password,log_level='DEBUG')


def pack_shp(filename,output_filename):
    path = os.path.dirname(filename)
    shutil.make_archive(output_filename.replace('.zip',''), 'zip', path)
    print(output_filename)
    
    for rootDir, subdirs, filenames in os.walk(path):
        # Find the files that matches the given patterm
        for filename in filenames:
            try:
                if '.zip' not in filename: os.remove(os.path.join(rootDir, filename))
            except OSError:
                print("Error while deleting file")

    return output_filename    
    
def generate_grid_file(count,filename, lat, lon):
    
    # create output file
    outDriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(filename):
        os.remove(filename)
    outDataSource = outDriver.CreateDataSource(filename)
    outLayer = outDataSource.CreateLayer(filename,geom_type=ogr.wkbPoint )
    featureDefn = outLayer.GetLayerDefn()
    
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(4326)

    spatialRef.MorphToESRI()
    file = open(filename.replace('.shp','.prj'), 'w')
    file.write(spatialRef.ExportToWkt())
    file.close()
    
    rows = math.ceil(count/100)
    cols = 100
    
    gridHeight = 0.001
    gridWidth = 0.001
    ringXleftOrigin = lat
    ringYtopOrigin = lon
    
    
    # create grid cells
    countcols = 0
    with alive_bar(cols) as bar:
        while countcols < cols:
            bar.text(str(count))
            
            countcols += 1
            countrows = 0
            
            ringYtop = ringYtopOrigin
            
            while countrows < rows:
                countrows += 1
                geom = ogr.Geometry(ogr.wkbPoint)
                geom.AddPoint(ringXleftOrigin, ringYtop)
                
                # add new geom to layer
                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(geom)
                outLayer.CreateFeature(outFeature)
                outFeature = None

                # new envelope for next poly
                ringYtop = ringYtop - gridHeight
                #ringYbottom = ringYbottom - gridHeight
                
            # new envelope for next poly    
            ringXleftOrigin = ringXleftOrigin + gridWidth
            bar()
            
    outDataSource = None

def generate_grids():


    mode1 = False
    mode2 = False
    mode3 = True

    featurecouns = list()
    featurecounts = (1000,2000,5000,10000,10000,20*1000,30*1000,40*1000,50*1000,50*1000,60*1000,70*1000,100*1000,200*1000,300*1000,400*1000,500*1000,800*1000)
    #featurecounts = (5000,5000)
    shift = 0
    
    group_lvl1 = ngwapi.create_resource_group(GROUP, display_name='upload_benchmark' , overwrite='truncate')
    
    curenttime = datetime.datetime.now()
    curenttime = curenttime.strftime('%Y%m%d_%H%M%S')
    csv_filename = os.path.join(STATISTICDIR,str(curenttime)+'.csv')
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['features','duration','result','mode'])
        
    with alive_bar(len(featurecounts)) as bar:
        for featurecount in featurecounts:
            shp_filename = os.path.join(DIR,str(featurecount)+'.shp')
            zip_filename = os.path.join(DATADIR,str(featurecount)+'.zip')
            if os.path.exists(DIR) and os.path.isdir(DIR): 
                shutil.rmtree(DIR)
            os.mkdir(DIR)
	        
            shift = shift + (featurecount/100/2*0.001)+0.001
            bar.text(str(featurecount))
            generate_grid_file(featurecount,shp_filename,37.666 + shift,55.666)
            bar()
	
            if mode2 == True:
                group_id = ngwapi.create_resource_group(group_lvl1, display_name='upload_benchmark '+str(featurecount)+' 2 '+ngwapi.generate_name(), overwrite='truncate')
                execution_result = True
                bar.text('uploading '+str(featurecount))
                start_time = time.time()
                try:
                    ngwapi.upload_vector_layer_ogr2ogr(shp_filename,group_id, display_name=str(featurecount)+'.zip')
                except:
                    execution_result = False
                end_time = time.time()
                execute_seconds = end_time-start_time
                print(featurecount,  math.ceil(execute_seconds),execution_result)
                with open(csv_filename, 'a', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)                
                    csvwriter.writerow([featurecount,math.ceil(execute_seconds),execution_result,2])
                   
            if mode1 == True:
                layer_path = pack_shp(shp_filename,zip_filename)
                
                group_id = None
                while group_id is None:
                    try:
                        group_id = ngwapi.create_resource_group(group_lvl1, display_name='upload_benchmark '+str(featurecount)+' 1 '+ngwapi.generate_name(), overwrite='truncate')
                    except:
                        group_id = None
                        time.sleep(5)
                execution_result = True
                bar.text('uploading '+str(featurecount))
                start_time = time.time()
                try:
                    ngwapi.upload_vector_layer(zip_filename,group_id, display_name=str(featurecount)+'.zip FILE_UPLOAD POST')
                except:
                    execution_result = False
                end_time = time.time()
                execute_seconds = end_time-start_time
                print(featurecount,  math.ceil(execute_seconds),execution_result)
                with open(csv_filename, 'a', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)                
                    csvwriter.writerow([featurecount,math.ceil(execute_seconds),execution_result,1])
                    
            if mode3 == True:
                layer_path = pack_shp(shp_filename,zip_filename)
                
                group_id = None
                while group_id is None:
                    try:
                        group_id = ngwapi.create_resource_group(group_lvl1, display_name='upload_benchmark '+str(featurecount)+' 3 TUS '+ngwapi.generate_name(), overwrite='truncate')
                    except:
                        group_id = None
                        time.sleep(5)
                assert group_id is not None
                execution_result = True
                bar.text('uploading '+str(featurecount)+' tus')
                start_time = time.time()
                try:
                
                    ngwapi.upload_vector_layer_tus(zip_filename,group_id, display_name=str(featurecount)+'.zip TUS')
                
                except:
                    execution_result = False
                end_time = time.time()
                execute_seconds = end_time-start_time
                print(featurecount,  math.ceil(execute_seconds),execution_result,'mode 3')
                with open(csv_filename, 'a', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)                
                    csvwriter.writerow([featurecount,math.ceil(execute_seconds),execution_result,3])
                
       
        
if __name__ == "__main__":

    generate_grids()    
    
