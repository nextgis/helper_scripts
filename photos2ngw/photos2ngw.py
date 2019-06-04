# -*- coding: UTF-8 -*-

import os, sys
import exifread
import json

try:
    import config
except ImportError:
    print "config.py not found. Copy config.example.py to config.py, and set creds here. See readme.md"
    quit()
    
    
def get_args():
    import argparse
    p = argparse.ArgumentParser(description='Move images to folder with his date')
    p.add_argument('--resource_id', help='nextgis.com folder id', type=int)
    p.add_argument('--debug', '-d', help='debug mode')
    p.add_argument('path', help='Path to folder containing JPG files')
    return p.parse_args()

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None
    
   

def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)
    
def get_exif_location(exif_data):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    lat = None
    lon = None

    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

    return lat, lon
    

if __name__ == '__main__':
    args = get_args()
    file_list = []
    for root, sub_folders, files in os.walk(args.path):
        for name in files:
            file_list += [os.path.join(root, name)  ]

    index = 0
    IterationStep = 1
    total = len(file_list)
    
    geojson = dict()
    geojson['type']='FeatureCollection'
    geojsonFeatures = list()
    while index < total:
        filename = file_list[index]
		
        file = open(filename, 'rb')
        tags = exifread.process_file(file, details=False)
        file.close()

        lat, lon = get_exif_location(tags)
        geojsonFeature = dict()
        geojsonFeature['type'] = 'Feature'
        geojsonFeature['crs'] = dict()
        geojsonFeature['crs']['type'] = 'name'
        geojsonFeature['crs']['properties'] = dict()
        geojsonFeature['crs']['properties']['name'] = "urn:ogc:def:crs:OGC:1.3:CRS84"
        geojsonFeature['properties'] = dict()
        geojsonFeature['properties']['filename'] = filename
        geojsonFeature['properties']['datetime'] = str(_get_if_exist(tags,'Image DateTime'))
        geojsonFeature['geometry']=dict()
        geojsonFeature['geometry']['type'] = 'Point'
        geojsonFeature['geometry']['coordinates'] = [lon,lat]
        

        if lat is not None and lon is not None :
            
            geojsonFeatures.append(geojsonFeature)
                
        index = index+IterationStep
        if index > total:
            index=total
        progress(index, len(file_list), status='Create geojson with photo locations, total = '+str(total))
        
    geojson['features'] = geojsonFeatures
    
    filename = 'photos.geojson'
    with open('photos.geojson', 'w') as outfile:  
        json.dump(geojson, outfile)


    URL = config.ngw_url
    AUTH = config.ngw_creds
    GRPNAME = "photos"

    import requests
    from json import dumps
    from datetime import datetime


    # Пока удаление ресурсов не работает, добавим дату и время к имени группы
    GRPNAME = datetime.now().isoformat() + " " + GRPNAME

    s = requests.Session()


    def req(method, url, json=None, **kwargs):
        """ Простейшая обертка над библиотекой requests c выводом отправляемых
        запросов в stdout. К работе NextGISWeb это имеет малое отношение. """

        jsonuc = None

        if json:
            kwargs['data'] = dumps(json)
            jsonuc = dumps(json, ensure_ascii=False)

        req = requests.Request(method, url, auth=AUTH, **kwargs)
        preq = req.prepare()

        print ""
        print ">>> %s %s" % (method, url)

        if jsonuc:
            print ">>> %s" % jsonuc

        resp = s.send(preq)

        print resp.status_code
        assert resp.status_code / 100 == 2

        jsonresp = resp.json()

        for line in dumps(jsonresp, ensure_ascii=False, indent=4).split("\n"):
            print "<<< %s" % line

        return jsonresp

    # Обертки по именам HTTP запросов, по одной на каждый тип запроса

    def get(url, **kwargs): return req('GET', url, **kwargs)            # NOQA
    def post(url, **kwargs): return req('POST', url, **kwargs)          # NOQA
    def put(url, **kwargs): return req('PUT', url, **kwargs)            # NOQA
    def delete(url, **kwargs): return req('DELETE', url, **kwargs)      # NOQA

    # Собственно работа с REST API

    iturl = lambda (id): '%s/api/resource/%d' % (URL, id)
    courl = lambda: '%s/api/resource/' % URL

    if args.resource_id is None:
    	# Создаем группу ресурсов внутри основной группы ресурсов, в которой будут
    	# производится все дальнешние манипуляции.
    	grp = post(courl(), json=dict(
    		resource=dict(
    			cls='resource_group',   # Идентификатор типа ресурса
    			parent=dict(id=0),      # Создаем ресурс в основной группе ресурсов
    			display_name=GRPNAME,   # Наименование (или имя) создаваемого ресурса
    		)
    	))

		# Поскольку все дальнейшие манипуляции будут внутри созданной группы,
		# поместим ее ID в отдельную переменную.
        grpid = grp['id']
    else:
        grpid = args.resource_id
    grpref = dict(id=grpid)


    # Метод POST возвращает только ID созданного ресурса, посмотрим все данные
    # только что созданной подгруппы.
    get(iturl(grpid))


    # Проходим по файлам, ищем geojson

        
    print "uploading "+filename
            
            # Теперь создадим векторный слой из geojson-файла. Для начала нужно загрузить
            # исходный ZIP-архив, поскольку передача файла внутри REST API - что-то
            # странное. Для загрузки файлов предусмотрено отдельное API, которое понимает
            # как обычную загрузку из HTML-формы, так загрузку методом PUT. Последнее
            # несколько короче.
    with open(filename, 'rb') as fd:
        shpzip = put(URL + '/api/component/file_upload/upload', data=fd)


        srs = dict(id=3857)


        vectlyr = post(courl(), json=dict(
                resource=dict(cls='vector_layer', parent=grpref, display_name=os.path.splitext(filename)[0]),
                vector_layer=dict(srs=srs, source=shpzip)
            ))

        #Создание стиля
        vectstyle = post(courl(), json=dict(
                resource=dict(cls='mapserver_style', parent=vectlyr, display_name=os.path.splitext(filename)[0]),
                mapserver_style=dict(xml='''<map><symbol><type>ellipse</type><name>circle</name><points>1 1</points> 
  <filled>true</filled>  </symbol><layer><class><style><symbol>circle</symbol><color red="255" green="0" blue="189"/>
  <outlinecolor red="255" green="0" blue="0"/></style></class></layer></map>''')
            ))
    outfile.close()
    fd.close()
    os.remove(filename) 




            
