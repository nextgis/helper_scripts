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

#from pudb import set_trace; set_trace()

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



def message2status(stmessage):
    status=''
    if stmessage == u'Новый': status='1'
    elif stmessage == u'Подтвержден': status='2'
    elif stmessage == u'Не подтвержден': status='3'
    elif stmessage == u'Принят в работу': status='4'
    elif stmessage == u'Проводится проверка': status='5'
    elif stmessage == u'Удален': status='6'

    elif stmessage == u'Передано в полицию': status='7'
    elif stmessage == u'Возбуждено уголовное дело': status='8'
    elif stmessage == u'Отказано в возбуждении уголовного дела': status='9'

    elif stmessage == u'Усиливается': status='10'
    elif stmessage == u'Действует': status='11'
    elif stmessage == u'Ослабевает': status='12'
    elif stmessage == u'Не распространяется': status='13'
    elif stmessage == u'Локализован': status='14'
    elif stmessage == u'Возобновился': status='15'
    elif stmessage == u'Ликвидирован': status='16'
    elif stmessage == u'Тушение приостановлено решением КЧС': status='17'
    else: status=''
    return status




'''
Скрипт определяет время последнего запуска, читая файл last_update, если файла нет - то время последнего запуска назаначается 1990 годом
Если скрипт уже запускался сегодня, то скрипт останавливается.
Скрипт делает get-запрос на внешний сервер, команда updateObj, получает dict
Проход по dict
    Получается id фичи в ngw на основе внешних данных, если этой фичи нет в ngw, то id будет пустым
    Чего-то делается с атрибутами, полученными с внешнего сервера
    Создаётся новый payload с атрибутами, полученными с внешнего сервера
        update фича в ngw (этот скрипт не должен создавать фичи, только изменять их)

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




        # print regionStr


        payload = {
            'fields':
                {
                'stmessage': item.get('status'),
                'status': message2status(item.get('status'))
                }
            }

        if str(ngwFeatureId) == '':
            continue

        print payload
        req = requests.put(ngw_url + ngw_resourse_id + '/feature/' + str(ngwFeatureId), data=json.dumps(payload), auth=ngw_creds)
        print 'object id ' + str(objectId) + ' -- update feature #' + str(ngwFeatureId) + ' ' + str(req.status_code) + ' ' + str(req.url)

        #print req
        #print req.json()

    # save last run time
    with open('last_update', 'w') as f:
        f.write(datetime.now().isoformat() + 'Z')
        
