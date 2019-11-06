# Code snippets for imagery download

# Sentinel

## Download Sentinel-2 in python
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
## sentinel_unpack.sh
## Unpack Sentinel-2 scenes and crop by polygon in bash

открывает не все сцены, нужно добавить получение пути к субдатасету из gdalinfo, чтоб вытаскивалось EPSG


## Generate external previews for imagery

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

## Download Landsat-8
Его можно скачивать бесплатно с Amazon, а Sentinel оттуда - только за деньги.

Есть библиотека на python landsat-util, она же есть на докерхабе. 

https://pythonhosted.org/landsat-util/ 


## Unpack Landsat-8 scenes

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

## Landsat-8 bash download and panshaprering
```

BASE=LC08_L1TP_125025_20190409_20190422_01_T1
LN8_PATH=126
LN8_ROW=025
touch url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/${LN8_PATH}/${LN8_ROW}/${BASE}/${BASE}_B2.TIF" >> url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/${LN8_PATH}/${LN8_ROW}/${BASE}/${BASE}_B3.TIF" >> url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/${LN8_PATH}/${LN8_ROW}/${BASE}/${BASE}_B4.TIF" >> url.list
echo "http://landsat-pds.s3.amazonaws.com/c1/L8/${LN8_PATH}/${LN8_ROW}/${BASE}/${BASE}_B8.TIF" >> url.list
cat url.list | parallel -I% -j 8 wget  %

#see http://gis-lab.info/qa/landsat-tiles.html
gdal_landsat_pansharp -pan ${BASE}_B8.TIF -ndv 0 -o ${BASE}_pan.tif \
 -rgb ${BASE}_B4.TIF -rgb ${BASE}_B3.TIF -rgb ${BASE}_B2.TIF \
 -lum ${BASE}_B3.TIF 0.5 -lum ${BASE}_B4.TIF 0.5

gdaladdo  -r cubic -ro --config COMPRESS_OVERVIEW LZW ${BASE}_pan.tif

rm ${BASE}_B2.TIF
rm ${BASE}_B3.TIF
rm ${BASE}_B4.TIF
rm ${BASE}_B8.TIF
```

## Landsat-7 

Скрипт для выкачивания Landsat-5,7,8 c earthexplorer.usgs.gov по айдишникам
```
git clone https://github.com/olivierhagolle/LANDSAT-Download.git

cat > scenes.txt << EOF
moscow LE71790212000273SGS00
EOF

mkdir scenes
python LANDSAT-Download/download_landsat_scene.py -o liste -l $(pwd)/scenes.txt -u $(pwd)/usgs.txt --output scenes

```
