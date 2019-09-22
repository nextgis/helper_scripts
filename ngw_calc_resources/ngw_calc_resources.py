#Outputs a list of ids of resources for which permissions are set
#python ngw_check_permissions.py -u sandbox -r https -n administrator -p demodemo
#set([u'wmsclient_layer', u'postgis_connection', u'lookup_table', u'resource_group', u'wmsclient_connection', u'mapserver_style', u'vector_layer', u'raster_style', u'raster_layer', u'basemap_layer', u'wfsserver_service', u'tracker', u'webmap', u'trackers_group', u'wmsserver_service', u'formbuilder_form', u'qgis_vector_style', u'postgis_layer', u'collector_project'])

import requests
import argparse
from requests.auth import HTTPBasicAuth

parser = argparse.ArgumentParser()
parser.add_argument('-r','--protocol',default='http',help='http or https')
parser.add_argument('-u','--url', required=True, help='Web GIS name')
parser.add_argument('-n','--name', help='Username')
parser.add_argument('-p','--password', help='Password')
args = parser.parse_args()


url = '%s://%s.nextgis.com/api/resource/search/' % (args.protocol,args.url)
print(url)

items = requests.get(url, auth=HTTPBasicAuth(args.name,args.password)).json()

raster_layer = 0
raster_style = 0
resource_group = 0
postgis_connection = 0
qgis_vector_style = 0
mapserver_style = 0
vector_layer = 0
basemap_layer = 0
webmap = 0
postgis_layer = 0
lookup_table = 0
wfsserver_service = 0
wmsclient_layer = 0
trackers_group = 0
collector_project = 0
tracker = 0
wmsserver_service = 0
formbuilder_form = 0
wmsclient_connection = 0

for item in items:
    if item['resource']['cls'] == 'raster_layer':
        raster_layer += 1
    if item['resource']['cls'] == 'raster_style':
        raster_style += 1
    elif item['resource']['cls'] == 'resource_group':
        resource_group += 1
    elif item['resource']['cls'] == 'postgis_connection':
        postgis_connection += 1
    elif item['resource']['cls'] == 'qgis_vector_style':
        qgis_vector_style += 1
    elif item['resource']['cls'] == 'vector_layer':
        vector_layer += 1
    elif item['resource']['cls'] == 'basemap_layer':
        basemap_layer += 1
    elif item['resource']['cls'] == 'webmap':
        webmap += 1
    elif item['resource']['cls'] == 'postgis_layer':
        postgis_layer += 1
    elif item['resource']['cls'] == 'mapserver_style':
        mapserver_style += 1
    elif item['resource']['cls'] == 'lookup_table':
        lookup_table += 1
    elif item['resource']['cls'] == 'wfsserver_service':
        wfsserver_service += 1
    elif item['resource']['cls'] == 'wmsserver_service':
        wmsserver_service += 1
    elif item['resource']['cls'] == 'wmsclient_layer':
        wmsclient_layer += 1
    elif item['resource']['cls'] == 'trackers_group':
        trackers_group += 1
    elif item['resource']['cls'] == 'tracker':
        tracker += 1
    elif item['resource']['cls'] == 'collector_project':
        collector_project += 1
    elif item['resource']['cls'] == 'formbuilder_form':
        formbuilder_form += 1
    elif item['resource']['cls'] == 'wmsclient_connection':
        wmsclient_connection += 1
        
agg = raster_layer + vector_layer + webmap + postgis_layer + wmsclient_layer

print('Aggregated: ' + str(agg))

print('Raster layers: ' + str(raster_layer))
print('    Raster styles: ' + str(raster_style))
print('Vector layers: ' + str(vector_layer))
print('    Vector styles (QGIS): ' + str(qgis_vector_style))
print('    Vector styles (MapServer): ' + str(mapserver_style))
print('PostGIS connections: ' + str(postgis_connection))
print('WMS connections: ' + str(wmsclient_connection))
print('PostGIS layers: ' + str(postgis_layer))
print('WFS services: ' + str(wfsserver_service))
print('WMS services: ' + str(wmsserver_service))
print('WMS layers: ' + str(wmsclient_layer))
print('Trackers: ' + str(tracker))
print('Trackers groups: ' + str(trackers_group))
print('Resources groups: ' + str(resource_group))
print('Webmaps: ' + str(webmap))
print('Basemaps: ' + str(basemap_layer))
print('Collector projects: ' + str(collector_project))
print('Formbuilder forms: ' + str(formbuilder_form))
print('Looukup tables: ' + str(lookup_table))