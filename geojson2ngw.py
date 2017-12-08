# -*- coding: utf-8 -*-

'''
Upload all geojson from folder into NextGISWeb as new layers, and create simple mapserver styles

Usage: geojson2ngw.py foldername

Example: python geojson2ngw.py --login admin --password pass --groupname NEW --parent 499 --folder d:\Thematic\histgeo\ --url http://dev.nextgis.com/practice2
'''
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')


from __future__ import unicode_literals
import os

URL = 'http://example.com/ngw'
AUTH = ('administrator', 'admin')
GRPNAME = "Загрузка из python"

import requests
from json import dumps
from datetime import datetime


import argparse
def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Upload all geojson from folder into NextGISWeb as new layers, and create of simple mapserver style.',
            formatter_class=PrettyFormatter)
    parser.add_argument('--url', type=str,required=True, 
                           help='NGW instance url')
    parser.add_argument('--login', default='administrator', required=False, help = 'ngw login')
    parser.add_argument('--password', default='admin', required=False, help = 'ngw password')
    parser.add_argument('--parent', type=int, help='id of group', default=0, required=False)
    parser.add_argument('--groupname', type=str, help='name of new group', default='RESTUPL', required=False)
    parser.add_argument('--folder', help = 'Take all geojsons from this folder')



    parser.epilog = \
        '''Samples: 

#upload all geojsons from current folder
time python %(prog)s --url http://trolleway.nextgis.com --parent 19 --login administrator --password admin 

''' \
        % {'prog': parser.prog}
    return parser

parser = argparser_prepare()
args = parser.parse_args()

URL = args.url
AUTH = (args.login, args.password)
GRPNAME = args.groupname

if args.folder is None: 
    destdir = os.curdir
else:
    destdir = args.folder
PARENT=args.parent

# Пока удаление ресурсов не работает, добавим дату и время к имени группы
GRPNAME = GRPNAME + " " + datetime.now().isoformat()

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
        parent=dict(id=PARENT),      # Создаем ресурс в основной группе ресурсов
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

files = filter(os.path.isfile, os.listdir( destdir ) )
for dirpath, dnames, fnames in os.walk(destdir):
    for filename in fnames:
        if '.geojson'.lower() in filename.lower():
            filepath = (os.path.join(dirpath, filename))   
            print "uploading "+filename
            
            # Теперь создадим векторный слой из geojson-файла. Для начала нужно загрузить
            # исходный ZIP-архив, поскольку передача файла внутри REST API - что-то
            # странное. Для загрузки файлов предусмотрено отдельное API, которое понимает
            # как обычную загрузку из HTML-формы, так загрузку методом PUT. Последнее
            # несколько короче.
            with open(filepath, 'rb') as fd:
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
