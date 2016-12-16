from osgeo import ogr,osr
import csv
import os

f_output = open('output.csv','wb')
fieldnames_data = ('NAME','GTYPE','PROJECTION','COUNT')
csvwriter_output = csv.DictWriter(f_output, fieldnames=fieldnames_data)

ff = []
for (dirpath, dirnames, filenames) in os.walk('.'):
    for filename in filenames:
        if filename.endswith('.tab'.upper()): 
            ff.append(os.sep.join([dirpath, filename]))

for f in ff:
    print(f.decode('cp1251'))
    ogrData = ogr.Open(f.decode('cp1251'), False)
    layer = ogrData[0]
    count = layer.GetFeatureCount()
    prj = layer.GetSpatialRef().ExportToWkt()
    
    srs = osr.SpatialReference(wkt=prj)
    if srs.IsProjected() != 0:
        projection = srs.GetAttrValue('PROJECTION')
    else:
        projection = "Geographic"

    gtype = layer.GetGeomType()
    
    csvwriter_output.writerow(dict(NAME=f,
                                      GTYPE=ogr.GeometryTypeToName(gtype),
                                      PROJECTION=projection,
                                      COUNT=count))
   
