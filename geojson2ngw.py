# -*- coding: utf-8 -*-
'''
Upload all geojson from folder into NextGISWeb as new layers, and create simple mapserver styles

Usage: geojson2ngw.py foldername

Example: python geojson2ngw.py --login admin --password pass --groupname NEW --parent 499 --folder d:\Thematic\histgeo\ --url http://dev.nextgis.com/practice2
'''



from __future__ import unicode_literals
import os

URL = 'http://example.com/ngw'
AUTH = ('administrator', 'admin')
DEFAULT_GRPNAME = "Загрузка из Python"

import requests
from json import dumps
from datetime import datetime

import sys  
import os

reload(sys)  
sys.setdefaultencoding('utf8')

import argparse
def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 45

    parser = argparse.ArgumentParser(description='Upload all geojson from folder into NextGISWeb as new layers, and create of simple mapserver style.',
            formatter_class=PrettyFormatter)
    parser.add_argument('--url', type=str,required=False, help='NGW instance url')
    parser.add_argument('--login', default='administrator', required=False, help = 'ngw login')
    parser.add_argument('--password', default='admin', required=False, help = 'ngw password')
    parser.add_argument('--parent', type=int, help='id of parent group', default=0, required=False)
    parser.add_argument('--groupname', type=str, help='name of new group. Create only if parent=0', default=DEFAULT_GRPNAME, required=False)
    parser.add_argument('--folder', help = 'Take all geojsons from this folder')
    creating_group_parser = parser.add_mutually_exclusive_group(required=False)
    creating_group_parser.add_argument('--create', dest='create', help = 'Create new resourse group', action='store_true',default=True)
    creating_group_parser.add_argument('--no-create', dest='create', help = 'Upload layers into existing resourse group', action='store_false',default=False)





    parser.epilog = \
        '''Samples: 

#upload all geojsons from current folder
time python %(prog)s --url http://trolleway.nextgis.com --parent 19 --login administrator --password admin 

''' \
        % {'prog': parser.prog}
    return parser
    
def run_user_interface(parser=None):
    #simple user interface
    #get default values from parser object
    print 'Upload all geojson from folder into NextGISWeb as new layers, and create of simple mapserver style.'
    url = raw_input("NGW instance url with protocol: ")
    login = raw_input("NGW instance login: ")
    password = raw_input("NGW instance password: ")
    group_id = raw_input("NGW target group id: ")
    group_name = raw_input("NGW tager group name (0=don't create group: ")
    command = None
    while command not in (0,1):
        dir1 = os.path.dirname(os.path.realpath(__file__))
        command = raw_input('Source folder? 0='+os.path.dirname(os.path.realpath(__file__))+', 1=manual input ')
        try: 
            command = int(command)
        except ValueError:
            command = None
    if command == 0:
        folder = os.path.dirname(os.path.realpath(__file__))
    else:
        folder = raw_input('Enter folder path: ')
        
    results = dict()
    results['url'] = url
    results['login'] = login
    results['password'] = password
    results['folder'] = folder
    results['group_id'] = group_id
    results['group_name'] = group_name
    
    return results
    
parser = argparser_prepare()
args = parser.parse_args()



#if none arguments, run user interface
if args.url == None:
    user_commands = run_user_interface(parser)
    results=user_commands
    
    URL = results['url']
    AUTH = (results['login'], results['password'])
    groupname = args.groupname
    PARENT=args.parent
    destdir = results['folder']
    #end of user interface
    create = True
else:
    URL = args.url
    AUTH = (args.login, args.password)
    groupname = args.groupname #тут передаётся в переменную groupname, а потом 
    PARENT=args.parent
    if args.folder is None: 
        destdir = os.curdir
    else:
        destdir = args.folder

    create = args.create

args = None #don't use afterwards

# Что бы не было попыток создать несколько групп с одинаковым именем, добавим дату и время к имени группы
if groupname == DEFAULT_GRPNAME:
    GRPNAME = DEFAULT_GRPNAME + " " + datetime.now().isoformat()
else:
    GRPNAME = groupname

s = requests.Session()

def req(method, url, json=None, **kwargs):
    """ Простейшая обертка над библиотекой requests c выводом отправляемых
    запросов в stdout. К работе NextGISWeb это имеет малое отношение. """

    jsonuc = None

    if json:
        kwargs['data'] = dumps(json)
        jsonuc = dumps(json, ensure_ascii=False)

    req = requests.Request(method, url, auth=AUTH, timeout=None, **kwargs)
    preq = req.prepare()

    print ""
    print ">>> %s %s" % (method, url)

    if jsonuc:
        print ">>> %s" % jsonuc

    resp = s.send(preq)

    #assert resp.status_code / 100 == 2 , 'HTTP CODE ' + str(resp.status_code)

    try:
        jsonresp = resp.json()
    except:
        print 'bad response'
        print resp
        raise
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

if create:
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
else:
    #не создаём группу, а грузим файлы в существующую
    grpid = PARENT
    grpref = dict(id=grpid)    

# Метод POST возвращает только ID созданного ресурса, посмотрим все данные
# только что созданной подгруппы.
get(iturl(grpid))

upload_styles_responses = list()

# Проходим по файлам, ищем geojson

files = filter(os.path.isfile, os.listdir( destdir ) )
for dirpath, dnames, fnames in os.walk(destdir):
    for filename in fnames:
        print repr(filename)
        if ('.geojson' in repr(filename)) or ('.GEOJSON' in repr(filename)): #use lower finction to filename casue fail at cyrilic filename
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
            upload_styles_responses.append(vectstyle)
            
# iterate through files, search for tiff 

files = filter(os.path.isfile, os.listdir( destdir ) )
for dirpath, dnames, fnames in os.walk(destdir):
    for filename in fnames:
        print repr(filename)
        if ('.tif' in repr(filename)) or ('.TIF' in repr(filename)): #use lower finction to filename casue fail at cyrilic filename
            filepath = (os.path.join(dirpath, filename))   
            print "uploading "+filename
            
            # Upload raster file
            with open(filepath, 'rb') as fd:
                tif = put(URL + '/api/component/file_upload/upload', data=fd)


            # ???
            srs = dict(id=3857)

            # Query for create layer
            rastlyr = post(courl(), json=dict(
                resource=dict(cls='raster_layer', parent=grpref, display_name=os.path.splitext(filename)[0]),
                raster_layer=dict(srs=srs, source=tif)
            ))

            #Query for create style
            rasterstyle = post(courl(), json=dict(
                resource=dict(cls='raster_style', parent=rastlyr, display_name=os.path.splitext(filename)[0]),
                
            ))
            upload_styles_responses.append(vectstyle)
            
for style in upload_styles_responses:
    print style['resource']['id']
    
#vectlyr['id']
