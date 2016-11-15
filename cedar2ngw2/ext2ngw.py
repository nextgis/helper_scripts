# -*- coding: utf-8 -*-
import json
import requests
import pprint
import math
import os
import config

from datetime import datetime, date, time
from requests.auth import HTTPDigestAuth
from dateutil.parser import parse

# new API citorus
# http://91.239.143.154/cedar/updateObj?begin=1990-01-01T00:00:00.000Z&end=2015-09-21T00:00:00.000Z
# http://91.239.143.154/cedar/updateObj?begin="1990-12-31T00:00:00.000Z"&end="2015-08-18T00:00:00.000Z"
# response: {"objectID":"A4754895o21052o63814o14197o799578","number":3266,"source":"Веб-GIS","sourceID":13767,"applicant":"","controller":"","region":{"key":"","value":"Приморский край"},"district":"","city":"","landmarks":"","forestery":"Рощинское","precinct":"Таежное","territory":[{"vydel":46}],"geo":[136.404910714,46.008964285699925],"violations":[],"description":"","species":"","date":"2015-09-18T00:00:00.000Z","time":"00:00","area":"","status":"Новое лесоизменение"}
# http://176.9.38.120/fv/api/resource/57?objectID=A4754895o21052o63814o14197o799578
# last cedar API
# http://91.239.143.154/cedar/updateObj?begin=2015-10-10T00:00:00.000Z&end=2015-10-20T00:00:00.000Z

dict_url = config.dict_url
dict_creds = config.dict_creds

ngw_url = config.ngw_url
ngw_creds = config.ngw_creds
timeout = config.timeout
ngw_resourse_id=config.ngw_resourse_id

earthRadius = 6378137.0

def wgs84ToMercatorSphereX(x):
    return earthRadius * math.radians(x)

def wgs84ToMercatorSphereY(y):
    return earthRadius * math.log(math.tan(math.pi / 4 + math.radians(y) / 2))

def parseGeom(geodict):
    if geodict[0] < -180 or geodict[0] > 180 or geodict[1] < -90 or geodict[1] > 90:
        return None
#    firstVal = geodict[0]
#    if type(firstVal) is float:
    geom = 'MULTIPOINT ('
    geom += str(wgs84ToMercatorSphereX(float(geodict[0])))
    geom += u' '
    geom += str(wgs84ToMercatorSphereY(float(geodict[1])))
    geom += ')'
    return geom
#    else:
#        geom = 'MULTIPOINT ('
#        geosubdict = firstVal
#        for geoitem in geosubdict:
#           if geom != 'MULTIPOINT (':
#               geom += ', '
#           geom += str(wgs84ToMercatorSphereX(float(geoitem[0])))
#           geom += u' '
#           geom += str(wgs84ToMercatorSphereY(float(geoitem[1])))
#        geom += ')'
#        return geom

def getFeatureIdforObjectId(objectId):
#    print "get url: " + ngw_url + '57/feature/?objectID=' + objectId
    try:
        req = requests.get(ngw_url + ngw_resourse_id+'/feature/?objectID=' + objectId, auth=ngw_creds)
        req.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print err
        import sys
        sys.exit(1)

    try:
        dictionary = req.json()
        for item in dictionary:
            return item.get('id')
    except Exception:
        print 'json error'
        print req        
    return None

def message2status(stmessage):
    status=''
    if stmessage == u'Новый': status='1'
    elif stmessage == u'Принят в работу': status='4'
    elif stmessage == u'Проводится проверка': status='5'
    elif stmessage == u'Проводится проверка': status='5'
    else: status='99999'
    return status





'''
Скрипт определяет время последнего запуска, читая файл last_update, если файла нет - то время последнего запуска назаначается 1990 годом
Если скрипт уже запускался сегодня, то скрипт останавливается.
Скрипт делает get-запрос на внешний сервер, команда updateObj, получает dict
Проход по dict
    Кастомным GET запросом к ngw получается атрибут id по атрибуту objectID.
    Чего-то делается с атрибутами, полученными с внешнего сервера
    Создаётся новый payload с атрибутами, полученными с внешнего сервера
    Если полученный id фичи пустой, то 
        создаётся новая фича в ngw
    если id фичи есть, то
        update фича в ngw

В файл last_update записывается текущее время 
'''

if __name__ == '__main__':

    # read last script run timestamp
    if os.path.isfile('last_update'):
        with open('last_update', 'r') as f:
           lastDtStr = f.read()
    # or set it to default value
    else:
        lastDtStr = "1990-01-01T00:00:00.000Z"

    nowDtStr = datetime.now().isoformat() + 'Z';

    lastDt = parse(lastDtStr)
    nowDt = parse(nowDtStr)

    if lastDt.year == nowDt.year and lastDt.month == nowDt.month and lastDt.day == nowDt.day:
        print 'already worked today! let me relax please!'
        exit()

    srsUrl = dict_url + '/cedar/updateObj' + '?begin=' + lastDtStr + '&end=' + nowDtStr
    print srsUrl

    req = requests.get(srsUrl, auth=HTTPDigestAuth(*dict_creds))
    dictionary = req.json()

    # pp = pprint.PrettyPrinter(indent=4)

    for item in dictionary:
        #pp.pprint(item)

        # check if update or insert
        #print item
        #print
        ngwFeatureId = item.get('sourceID')
        objectId = item.get('sourceID')

        if item.get('geo') is None:
            continue

        geom = parseGeom(item.get('geo'))
        if geom is None:
            continue


        # print regionStr


        payload = {
            'geom': geom,
            'fields':
                {
                'stmessage': item.get('status'),
                'status': message2status(item.get('status'))
                }
            }

        if str(ngwFeatureId) == '':
            continue

        print payload
        if ngwFeatureId is None:
            print 'object id ' + objectId + ' -- insert new feature' + ' ' + req.status_code
            req = requests.post(ngw_url + ngw_resourse_id + '/feature/', data=json.dumps(payload), auth=ngw_creds)
        else:
            req = requests.put(ngw_url + ngw_resourse_id + '/feature/' + str(ngwFeatureId), data=json.dumps(payload), auth=ngw_creds)
            print 'object id ' + str(objectId) + ' -- update feature #' + str(ngwFeatureId) + ' ' + req.status_code

        #print req
        #print req.json()

    # save last run time
    with open('last_update', 'w') as f:
        f.write(datetime.now().isoformat() + 'Z')
        
