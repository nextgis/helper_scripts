# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

URL = 'http://example.com/ngw'
AUTH = ('administrator', 'admin')
GRPNAME = "Загрузка из python"

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
grpref = dict(id=grpid)


# Метод POST возвращает только ID созданного ресурса, посмотрим все данные
# только что созданной подгруппы.
get(iturl(grpid))


# Проходим по файлам, ищем geojson

destdir = os.curdir 
files = filter(os.path.isfile, os.listdir( destdir ) )
for filename in files:
    if '.geojson'.lower() in filename.lower():    
        print "uploading "+filename
        
        # Теперь создадим векторный слой из geojson-файла. Для начала нужно загрузить
        # исходный ZIP-архив, поскольку передача файла внутри REST API - что-то
        # странное. Для загрузки файлов предусмотрено отдельное API, которое понимает
        # как обычную загрузку из HTML-формы, так загрузку методом PUT. Последнее
        # несколько короче.
        with open(filename, 'rb') as fd:
            shpzip = put(URL + '/api/component/file_upload/upload', data=fd)


        # Пока поддержка различных систем координат толком не реализована, но для
        # создания слоя нужно указать хоть какую-то.
        srs = dict(id=3857)

        # Теперь непосредственно создание слоя, в целом оно точно так же как и создание
        # группы работает, но указывается другой класс ресурса + данные этого класса -
        # в нашем случае это система координат и исходный файл.
        vectlyr = post(courl(), json=dict(
            resource=dict(cls='vector_layer', parent=grpref, display_name=os.path.splitext(filename)[0]),
            vector_layer=dict(srs=srs, source=shpzip)
        ))

        #Создание стиля
        vectstyle = post(courl(), json=dict(
            resource=dict(cls='mapserver_style', parent=vectlyr, display_name=os.path.splitext(filename)[0]),
            mapserver_style=dict(xml="<map><layer><class><style><color red=\"255\" green=\"240\" blue=\"189\"/><outlinecolor red=\"255\" green=\"196\" blue=\"0\"/></style></class></layer></map>")
        ))

#vectlyr['id']
