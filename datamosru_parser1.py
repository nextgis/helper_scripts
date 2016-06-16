#!/usr/bin/python
# -*- coding: utf-8 -*-

#Парсер геоданных Адресного Реестра Москвы.
#Скачайте json c http://data.mos.ru/opendata
#Положите его под именем "Остановки наземного городского пассажирского транспорта.json" в папку со скриптом
#python parcer.py
#Сгенерируется csv, который можно открыть в QGIS.
#Пларируется этот скрипт дописать до того, что бы он открывал любой слой с портала, и читал из метаданных его атрибуты


import ijson
import os
from shapely.geometry import Polygon, MultiPolygon, Point



csvFileName='busstops'


def RemoveDuplicatedNodes(coords):
    newCoords=[]
    for x,y in coords:
        if ((x,y) in newCoords) == False:
            newCoords.append((x,y))
    return newCoords


'''
[  
      {  
         "Name":"Name",
         "Caption":"Наименование",
         "Visible":true,
         "Type":"STRING",
         "SubColumns":null
      },
      {  
         "Name":"Street",
         "Caption":"Наименование улицы, на которой находится остановка",
         "Visible":true,
         "Type":"STRING",
         "SubColumns":null
      },
      {  
         "Name":"AdmArea",
         "Caption":"Административный округ",
         "Visible":false,
         "Type":"DICTIONARY",
         "SubColumns":null
      },
      {  
         "Name":"District",
         "Caption":"Район",
         "Visible":false,
         "Type":"DICTIONARY",
         "SubColumns":null
      },
      {  
         "Name":"RouteNumbers",
         "Caption":"Маршруты",
         "Visible":true,
         "Type":"STRING",
         "SubColumns":null
      },
      {  
         "Name":"StationName",
         "Caption":"Название остановки",
         "Visible":false,
         "Type":"STRING",
         "SubColumns":null
      },
      {  
         "Name":"Direction",
         "Caption":"Направление",
         "Visible":true,
         "Type":"DICTIONARY",
         "SubColumns":null
      },
      {  
         "Name":"Pavilion",
         "Caption":"Наличие павильона",
         "Visible":true,
         "Type":"FLAG",
         "SubColumns":null
      },
      {  
         "Name":"OperatingOrgName",
         "Caption":"Балансодержатель остановки с павильоном",
         "Visible":false,
         "Type":"STRING",
         "SubColumns":null
      },
      {  
         "Name":"geoData",
         "Caption":"Геоданные",
         "Visible":false,
         "Type":"CATALOG",
         "SubColumns":[  
            {  
               "Name":"type",
               "Caption":"Тип",
               "Visible":false,
               "Type":"STRING",
               "SubColumns":null
            },
            {  
               "Name":"coordinates",
               "Caption":"Координаты",
               "Visible":false,
               "Type":"CATALOG",
               "SubColumns":null
            }
         ]
      },
      {  
         "Name":"global_id",
         "Caption":"global_id",
         "Visible":false,
         "Type":"NUMBER",
         "SubColumns":null
      }
   ]
'''


values={}

fs = open(csvFileName+'.csv','w')
fs.write('''"WKT","Наименование","Наименование улицы, на которой находится остановка","Административный округ","Район","Маршруты","Название остановки","Направление","Наличие павильона","Балансодержатель остановки с павильоном","global_id"'''+"\n")
fs.close()

f = open('Остановки наземного городского пассажирского транспорта.json','r')
parser = ijson.parse(f)
for prefix, event, value in parser:



    print prefix, event, value
    if  (prefix, event) == ('item', 'start_map'):
        values={}
        values['Name']=''
        values['Street']=''
        values['AdmArea']=''
        values['District']=''
        values['RouteNumbers']=''
        values['StationName']=''
        values['Direction']=''
        values['Pavilion']=''
        values['OperatingOrgName']=''
        values['global_id']=''
        values['Name']=''






    elif prefix == 'item.Cells.global_id':
        values['global_id']=str(value).encode('utf-8')

    elif (prefix, event) == ('item.Cells.Name', 'string'):
        values['Name']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.Street', 'string'):
        values['Street']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.AdmArea', 'string'):
        values['AdmArea']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.District', 'string'):
        values['District']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.RouteNumbers', 'string'):
        values['RouteNumbers']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.StationName', 'string'):
        values['StationName']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.Direction', 'string'):
        values['Direction']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.Pavilion', 'string'):
        values['Pavilion']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.OperatingOrgName', 'string'):
        values['OperatingOrgName']=value.encode('utf-8')
   




    elif (prefix, event) == ('item.Id', 'string'):
        values['datasetGUID']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.DMT', 'string'):
        values['nomerDoma']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.AdmArea.item', 'string'):
        values['admArea']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.KRT', 'string'):
        values['nomerKorpusa']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.STRT', 'string'):
        values['nomerStroenia']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.VLD', 'string'):
        values['priznakVladenia']=value.encode('utf-8')
    elif (prefix, event) == ('item.Cells.SOOR', 'string'):
        values['priznakSooruzenia']=value.encode('utf-8')

    elif (prefix, event) == ('item.Cells.geoData.type', 'string'):

        geomType=value
        coords_array=[]

    elif (prefix, event) == ('item.Cells.geoData.coordinates.item','number'): #тип геометрии - point
        #добавляем одну координату в массив
        coords_array.append(value)

    elif (prefix, event) == ('item.Cells.geoData.coordinates.item.item.item','number'): #тип геометрии - polygon
        #добавляем одну координату в массив
        coords_array.append(value)
        #print '#='+str(value)
    elif (prefix, event) == ('item.Cells.geoData.coordinates.item.item.item.item','number'): #тип геометрии - multipolygon
        #добавляем одну координату в массив
        coords_array.append(value)


    elif (prefix, event) == ('item.Cells.geoData.coordinates', 'end_array'):
        coordsForShapely=[]
        for i in xrange(0,len(coords_array),2):
            coordsForShapely.append((coords_array[i],coords_array[i+1]))
        
        coordsForShapely=RemoveDuplicatedNodes(coordsForShapely)
        #Поскольку сейчас в исходном файле дырок в мультиполигонах не найдено, то все геометрии делаются полигонами.
        if geomType == 'Polygon':
            geom = Polygon(coordsForShapely)
        if geomType == 'MultiPolygon':
            geom = MultiPolygon(coordsForShapely)
        if geomType == 'Point':
            geom = Point(coordsForShapely)        

        #geom = Polygon(coordsForShapely)



        #модуль csv не работает с файлами открытыми на дозапись, поэтому генерирую строку csv вручную
        #export_values=(values['Полный адрес'].encode('utf-8'),values['Номер дома'].encode('utf-8'))
        export_string=''
        #for name, valueq in values:

        export_string += '"'+values['Name']+'",'
        export_string += '"'+values['Street']+'",'
        export_string += '"'+values['AdmArea']+'",'
        export_string += '"'+values['District']+'",'
        export_string += '"'+values['RouteNumbers']+'",'
        export_string += '"'+values['StationName']+'",'
        export_string += '"'+values['Direction']+'",'
        export_string += '"'+values['Pavilion']+'",'
        export_string += '"'+values['OperatingOrgName']+'",'
        export_string += '"'+values['global_id']+'",'


        print export_string

        fs = open(csvFileName+'.csv','a')
        fs.write(geom.wkt +','+ export_string+"\n")

        fs.close()
        print '=================================='





#generate vrt

txt='''<OGRVRTDataSource>
    <OGRVRTLayer name="'''+csvFileName+'''">
        <LayerSRS>WGS84</LayerSRS>
        <SrcDataSource>'''+csvFileName+'''.csv</SrcDataSource>
        <GeometryType>wkbPoint</GeometryType>
        <GeometryField encoding="PointFromColumns" x="Lon" y="Lat"/>
    </OGRVRTLayer>
</OGRVRTDataSource>'''
text_file = open(csvFileName+".vrt", "w")
text_file.write(txt)
text_file.close()

#convert to geojson using ogr2ogr

command='ogr2ogr -f "GeoJSON" '+csvFileName+'.geojson '+csvFileName+'.vrt'
print command
os.system(command)
