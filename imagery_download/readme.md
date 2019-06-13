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

```

path='/volume/'
ref='S2B_MSIL2A_20190529T032549_N0212_R018_T50UMA_20190529T064818'
cutlinepath='volume/aoi.geojson'


#открытие zip-архива Sentinel2, создание geotiff
time gdal_translate SENTINEL2_L2A:/vsizip/$path$ref.zip/$ref.SAFE/MTD_MSIL2A.xml:20m:EPSG_32650 $ref_stage1.tif -oo ALPHA=YES -co TILED=YES --config GDAL_CACHEMAX 1000 --config GDAL_NUM_THREADS AUTO

#вытаскивание конкретных каналов rgb
#каналы 3,2,1 это из subdataset2, канал 7 - альфа, созданный в предыдущем вызове gdal_translate
time gdal_translate  -b 3 -b 2 -b 1 -b 7 $ref_stage1.tif $ref_stage2.tif

#обрезка по полигону
time gdalwarp -dstalpha -overwrite -co COMPRESS=LZW -cutline $cutlinepath -crop_to_cutline $ref_stage2.tif $path$ref.tif

rm $ref_stage1.tif
rm $ref_stage2.tif

```
