#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pprint
import requests
from requests.auth import HTTPBasicAuth
import datetime
import shutil
import json

import pyngw

import zipfile
#pip3 install --upgrade --force-reinstall git+https://github.com/nextgis/pyngw.git

import argparse
def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 35

    parser = argparse.ArgumentParser(description='Dublicate ngw resource group with webmaps and subgroups using recursion',
            formatter_class=PrettyFormatter)

    parser.add_argument('--url1', dest='url1', required=True)
    parser.add_argument('--login1', dest='login1', required=False, default='administrator')
    parser.add_argument('--password1', dest='password1', required=False, default='admin')
    parser.add_argument('--src', dest='src', required=True,  type=int, help='group id source')
    
    parser.add_argument('--url2', dest='url2', required=True)
    parser.add_argument('--login2', dest='login2', required=False, default='administrator')
    parser.add_argument('--password2', dest='password2', required=False, default='admin')
    parser.add_argument('--dst', dest='dst', required=True,  type=int, help='group id dest')
    
    
    parser.add_argument('--cache', dest='cache', action='store_true')
    parser.add_argument('--no-cache', dest='cache', action='store_false')
    parser.set_defaults(cache=False)
    return parser

parser = argparser_prepare()
args = parser.parse_args()
      

DIR = 'DUMPS'
if os.path.exists(DIR) and os.path.isdir(DIR):
    shutil.rmtree(DIR)
os.mkdir(DIR)

ngwapi1 = pyngw.Pyngw(ngw_url = args.url1, login = args.login1, password = args.password1,log_level='INFO')
SRC_GROUP = args.src

ngwapi2 = pyngw.Pyngw(ngw_url = args.url2, login = args.login2, password = args.password2)
DST_GROUP = args.dst


ngwapi2.truncate_group(DST_GROUP)


pp = pprint.PrettyPrinter()

ids_dict = {}

def get_ids_changes(ngwapi):
    pass
    
def change_webmap_children(children, ids_dict):
    """
    Take webmap payload dict. Change all "layer_style_id" values to new values. Part of webmap dublicate process.

    example:
    payload['webmap']['root_item']['children'][0]["layer_style_id"]=10
    ids_dict['10'] = 125
    
    ...
    return_payload['webmap']['root_item']['children'][0]["layer_style_id"]=125
    
    
    """
    new_element = {}
    new_list = []

    for element in children:
        if element['item_type'] == 'layer':
            new_element = element
            try:
                new_element['layer_style_id'] = ids_dict[element['layer_style_id']]
            except:
                continue
            del new_element['style_parent_id']
            new_list.append(new_element)
        if element['item_type'] == 'group':
            new_element = element
            new_element['children'] = change_webmap_children(element['children'],ids_dict)
            
            new_list.append(new_element)
    return new_list
def dublicate_webmap(ngwapi1,ngwapi2,SRC_WEBMAP,DST_GROUP,ids_dict):

    payload = ngwapi1.get_resource(SRC_WEBMAP)
    childrens = {}
    childrens = change_webmap_children(payload['webmap']['root_item']['children'],ids_dict)
    pp.pprint(childrens)
    new_webmap_id = ngwapi2.create_webmap(DST_GROUP,childrens,payload['resource']['display_name'])
    print('webmap crated '+ngwapi2.ngw_url+'/resource/'+str(new_webmap_id))
    return new_webmap_id


def copy_resource_prepare_payload(payload):
    ns = payload
    del payload['resource']['parent']
    del payload['resource']['id']
    del payload['resource']['permissions']
    del payload['resource']['scopes']
    del payload['resource']['owner_user']
    del payload['resource']['interfaces']
    del payload['resource']['children']
    del payload['resource']['creation_date']
    del payload['social']
    return ns

def dublicate_vector_struct(ngwapi1,ngwapi2,SRC_LAYER,DST_GROUP):

    def copy_vector_layer_prepare_payload(structure):
        ns = dict()
        ns['resource'] = {}
        ns['resource']['cls'] = structure['resource']['cls']
        ns['resource']['description'] = structure['resource']['description']
        ns['resource']['display_name'] = structure['resource']['display_name']
        ns['resource']['keyname'] = structure['resource']['keyname']
        ns['resource']['parent'] = structure['resource']['parent']

        ns['vector_layer'] = structure['vector_layer']
        ns['vector_layer']['fields'] = structure['feature_layer']['fields']
        ns['resmeta'] = structure['resmeta']
        return ns

    payload = ngwapi1.get_resource(SRC_LAYER)
    payload = copy_vector_layer_prepare_payload(payload)
    payload['resource']['parent'] = {'id':DST_GROUP}
    response = requests.post(ngwapi2.ngw_url+'/api/resource/', json=payload, auth=ngwapi2.ngw_creds )
    print(payload)
    layer_id = response.json()['id']
    print('copied layer '+payload['resource']['display_name'])
    return layer_id

def copy_group2group(ngwapi1,ngwapi2,SRC_GROUP,DST_GROUP):
    ids_dict = {}
    ngwapi2.truncate_group(DST_GROUP)

    #---resource_group
    resources = ngwapi1.get_childs_resources(SRC_GROUP)
    for element in resources:
        if (element['resource']['cls'] == 'resource_group'):
            src_subgroup = element['resource']['id']
            #if src_subgroup != 72: continue
            payload = element
            payload = copy_resource_prepare_payload(payload)
            payload['resource']['parent'] = {'id':DST_GROUP}
            response = requests.post(ngwapi2.ngw_url+'/api/resource/', json=payload, auth=ngwapi2.ngw_creds )
            dst_subgroup = response.json()['id'] 
            ids_dict[src_subgroup] = dst_subgroup  
            new_ids_dict = copy_group2group(ngwapi1,ngwapi2,src_subgroup,dst_subgroup)
            # ^^^^^^^^^ RECURSIVE CALL
            ids_dict = {**ids_dict , **new_ids_dict} #concat dicts
    #---copy vector layers in group

    resources = ngwapi1.get_childs_resources(SRC_GROUP)
    for element in resources:
        if (element['resource']['cls'] == 'vector_layer'):
            SRC_LAYER = element['resource']['id']
            print('- layer '+ngwapi1.ngw_url+'/resource/'+str(SRC_LAYER))
            if element['resource']['display_name'].startswith('!'):
                continue
            if ngwapi1.get_feature_count(SRC_LAYER) == 0: #empty layer - create new empty layer
                print('layer empty, dublicate structure process')
                new_resource_id = dublicate_vector_struct(ngwapi1,ngwapi2,SRC_LAYER,DST_GROUP)
            else: #layer with features - download geojson
                path = os.path.join(DIR,str(SRC_LAYER)+'.geojson')
                #ngwapi1.download_vector_layer(path,SRC_LAYER,format='GeoJSON',srs=4326,zipped=False)
                #---hack for this source server
                cmd = '''curl  -sS -o DUMPS/{id}.geojson -u {login}:{password} "{url}/api/resource/{id}/export?format=GeoJSON&srs=4326&zipped=False&fid=ngw_id&encoding=UTF-8"'''
                cmd = cmd.format(id=SRC_LAYER,url=ngwapi1.ngw_url,login=ngwapi1.login, password=ngwapi1.password)
                print(cmd)
                os.system(cmd)
                #---/hack for this source server
                display_name = element['resource']['display_name']
                try:
                    new_resource_id = ngwapi2.upload_vector_layer(filepath=path,group_id=DST_GROUP, display_name=display_name)
                except Exception as inst:
                    print('wrong data downloaded, layer not created '+display_name)
                    continue
            display_name = element['resource']['display_name']
            print('uploaded '+display_name)
            ids_dict[SRC_LAYER] = new_resource_id
            new_payload = {'resmeta':{'items':{'prev_id':SRC_LAYER}}}
            ngwapi2.update_resource_payload(new_resource_id,new_payload)
            
            
            #qml
            childs = ngwapi1.get_childs_resources(SRC_LAYER)
            for subelement in childs:
                if subelement['resource']['cls'] == 'qgis_vector_style':
                    SRC_STYLE = subelement['resource']['id']
                    path = os.path.join(DIR,str(SRC_STYLE))
                    display_name = subelement['resource']['display_name']
	                #ngwapi2.download_qgis_style(path,SRC_STYLE)
                    #---hack for this source server
                    cmd = '''curl  -sS -o DUMPS/{id} -u {login}:{password} "{url}/api/resource/{id}/qml"'''
                    cmd = cmd.format(id=SRC_STYLE,url=ngwapi1.ngw_url,login=ngwapi1.login, password=ngwapi1.password)
                    os.system(cmd)
                    #---/hack for this source server
                    new_style_id = ngwapi2.upload_qgis_style(path,new_resource_id,display_name=display_name)
                    #new_payload = {'qgis_vector_style':{'svg_marker_library':{'id':SVG_LIB}}}
                    #ngwapi2.update_resource_payload(new_style_id,new_payload)
                    new_payload = {'resmeta':{'items':{'prev_id':SRC_STYLE}}}
                    ngwapi2.update_resource_payload(new_style_id,new_payload)
                    ids_dict[SRC_STYLE] = new_style_id
                    
                                   
    #---webmap
    resources = ngwapi1.get_childs_resources(SRC_GROUP)
    for element in resources:
        if (element['resource']['cls'] == 'webmap'):
            src_webmap = element['resource']['id']
            
            dublicate_webmap(ngwapi1,ngwapi2,src_webmap,DST_GROUP,ids_dict)
    
    
    return ids_dict
            
new_ids_dict = copy_group2group(ngwapi1,ngwapi2,SRC_GROUP,DST_GROUP)   
ids_dict = {**ids_dict , **new_ids_dict} #concat dicts 
#dublicate_webmap(ngwapi1,ngwapi2,2825,DST_GROUP,ids_dict)        


with open('ids.json', 'w') as fp:
    json.dump(ids_dict, fp)
shutil.rmtree(DIR)




