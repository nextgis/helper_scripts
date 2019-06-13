# Code snippets for imagery download

# Sentinel

## download in python

## unpack and crop in bash

```

path='/volume/'
ref=S2B_MSIL2A_20190529T032549_N0212_R018_T50UMA_20190529T064818


#открытие zip-архива Sentinel2, создание geotiff
time gdal_translate SENTINEL2_L2A:/vsizip/$path$ref.zip/$ref.SAFE/MTD_MSIL2A.xml:20m:EPSG_32650 $ref_stage1.tif -oo ALPHA=YES -co TILED=YES --config GDAL_CACHEMAX 1000 --config GDAL_NUM_THREADS AUTO

#вытаскивание конкретных каналов rgb
#каналы 3,2,1 это из subdataset2, канал 7 - альфа, созданный в предыдущем вызове gdal_translate
time gdal_translate  -b 3 -b 2 -b 1 -b 7 $ref_stage1.tif $ref_stage2.tif

#обрезка по полигоны
time gdalwarp -dstalpha -overwrite -co COMPRESS=LZW -cutline volume/aoi.geojson -crop_to_cutline $ref_stage2.tif $path$ref.tif


```
