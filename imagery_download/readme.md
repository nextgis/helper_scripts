# Code snippets for imagery download

# Sentinel

## download in python
Этот скрипт качает sentinel бесплатно (проверено в 2018-06), и сваливает их как zip-архивы
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

# connect to the API
api = SentinelAPI('login', 'passwords', 'https://scihub.copernicus.eu/dhus')

# download single scene by known product id


# search by polygon, time, and Hub query keywords
footprint = geojson_to_wkt(read_geojson('aoi.geojson'))
products = api.query(footprint,
                     date = ('20190302', date(2019, 05, 31)),
                     platformname = 'Sentinel-2',
                     cloudcoverpercentage = (0, 30))

# download all results from the search
api.download_all(products)

```
## unpack and crop in bash

открывает почему-то не все сцены
```

#!/bin/sh

path='volume/'
cutlinepath='volume/aoi.geojson'
for ref in $path*.zip
do
  scene=`echo $ref | sed 's/\.zip$//'`
  scene="$(basename -- $scene)"

  set -x
  #открытие zip-архива Sentinel2, создание geotiff
  gdal_translate SENTINEL2_L2A:/vsizip/$path$scene.zip/$scene.SAFE/MTD_MSIL2A.xml:20m:EPSG_32650 $scene-stage1.tif -oo ALPHA=YES -co TILED=YES --config GDAL_CACHEMAX 1000 --config GDAL_NUM_THREADS AUTO

  #вытаскивание конкретных каналов rgb
  #каналы 3,2,1 это из subdataset2, канал 7 - альфа, созданный в предыдущем вызове gdal_translate
  gdal_translate  -b 3 -b 2 -b 1 -b 7 $scene-stage1.tif $scene-stage2.tif

  #обрезка по полигону
  gdalwarp -dstalpha -overwrite -co COMPRESS=LZW -cutline $cutlinepath -crop_to_cutline $scene-stage2.tif $scene.tif
  
  gdaladdo -r cubic -ro  --config COMPRESS_OVERVIEW LZW $scene.tif
  rm $scene-stage1.tif
  rm $scene-stage2.tif
  echo ''

done

```

## Generate external previews

using parallel
```
sudo apt install parallel
time find . -name "*.tif" | parallel -I% --max-args 1 gdaladdo  -r cubic -ro  --config COMPRESS_OVERVIEW LZW % 
```
using loop

```
for scene in *.tif;do gdaladdo  -r cubic -ro  --config COMPRESS_OVERVIEW LZW $scene.tif;done
```

# Landsat

## Download
Его можно скачивать бесплатно с Amazon, а Sentinel оттуда - только за деньги.

Есть библиотека на python landsat-util, она же есть на докерхабе. 

https://pythonhosted.org/landsat-util/ 


## Unpack

один вариант
```
tar -xvzf community_images.tar.gz
gdal_merge.py  -separate LC81690372014137LGN00_B{4,3,2}.tif -o LC81690372014137LGN00_rgb.tif
```
другой вариант
```
#!/bin/sh

rm -f ln8
mkdir ln8
cd ln8
for zip in *.tar.gz
do
  dirname=`echo $zip | sed 's/\.tar.gz$//'`
  if mkdir "$dirname"
  then
    if cd "$dirname"
    then
      tar -xvzf  ../"$zip" --wildcards --no-anchored '*B8.TIF'
      cd ..
      # rm -f $zip # Uncomment to delete the original zip file
    else
      echo "Could not unpack $zip - cd failed"
    fi
  else
    echo "Could not unpack $zip - mkdir failed"
  fi
done

```

## Landsat-8 simple download and panshaprering
```
touch url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/125/025/LC08_L1TP_125025_20190409_20190422_01_T1/LC08_L1TP_125025_20190409_20190422_01_T1_B2.TIF" >> url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/125/025/LC08_L1TP_125025_20190409_20190422_01_T1/LC08_L1TP_125025_20190409_20190422_01_T1_B3.TIF" >> url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/125/025/LC08_L1TP_125025_20190409_20190422_01_T1/LC08_L1TP_125025_20190409_20190422_01_T1_B4.TIF" >> url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/125/025/LC08_L1TP_125025_20190409_20190422_01_T1/LC08_L1TP_125025_20190409_20190422_01_T1_B8.TIF" >> url.list
cat url.list | parallel -I% -j 8 wget  %
```
