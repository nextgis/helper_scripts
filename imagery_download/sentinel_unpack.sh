#!/bin/sh

path='../../'
cutlinepath='aoi.geojson'
for ref in $path*.zip
do
  scene=`echo $ref | sed 's/\.zip$//'`
  scene="$(basename -- $scene)"


  if [ -f "$scene.tif" ]; then
    echo "$scene aleadry exist"
    continue
  fi


  #set -x
  
  #получение пути к субдатасету
  subdataset=`gdalinfo -json $path$scene.zip  | jq -r '.metadata.SUBDATASETS.SUBDATASET_2_NAME'`
  echo $subdataset
   
  
  #открытие zip-архива Sentinel2, создание geotiff
  #gdal_translate SENTINEL2_L2A:/vsizip/$path$scene.zip/$scene.SAFE/MTD_MSIL2A.xml:20m:EPSG_32650 $scene-stage1.tif -oo ALPHA=YES -co TILED=YES --config GDAL_CACHEMAX 1000 --config GDAL_NUM_THREADS AUTO
  gdal_translate $subdataset $scene-stage1.tif -oo ALPHA=YES -co TILED=YES --config GDAL_CACHEMAX 1000 --config GDAL_NUM_THREADS AUTO


  #вытаскивание конкретных каналов rgb
  #каналы 3,2,1 это из subdataset2, канал 7 - альфа, созданный в предыдущем вызове gdal_translate
  gdal_translate  -b 3 -b 2 -b 1 -b 7 $scene-stage1.tif $scene-stage2.tif

  #обрезка по полигону
  gdalwarp -dstalpha -overwrite -co COMPRESS=LZW -cutline $cutlinepath -crop_to_cutline $scene-stage2.tif $scene.tif

  rm $scene-stage1.tif
  rm $scene-stage2.tif
  echo ''

done
