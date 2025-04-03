#!/usr/bin/env python
# -*- coding: utf-8 -*-
#******************************************************************************
#
# ngw_layer_copy.py
# ---------------------------------------------------------
# Dublicate structure of vector layer in ngw Web GIS
# More: https://gitlab.com/nextgis/helper_scripts
#
#
# Copyright (C) 2019-present Artem Svetlov (artem.svetlov@nextgis.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************


import argparse
import requests



def get_args():
    epilog = '''
    Dublicate structure of vector layer in ngw. Uses REST API query api/resource/
    This is a script intended for manual run before start ngw_replication, for full copy of layer sctucture, witch cannot be copied using geojson/shp.

    python ngw_layer_copy.py \
    --src_url http://dev.nextgis.com/sandbox/ --src_layer 1101 --src_login administrator --src_password demodemo \
    --dst_url http://dev.nextgis.com/sandbox/ --dst_gropup 1100 --dst_login administrator --dst_password demodemo
    '''
    p = argparse.ArgumentParser(description='Dublicate structure of vector layer in ngw', epilog = epilog)
    p.add_argument('--src_url', help='nextgis.com folder id', type=str, required=True)
    p.add_argument('--src_layer', help='nextgis.com folder id', type=int, required=True)
    p.add_argument('--src_login', help='nextgis.com folder id', type=str, required=True)
    p.add_argument('--src_password', help='nextgis.com folder id', type=str, required=True)
    p.add_argument('--dst_url', help='nextgis.com folder id', type=str, required=True)
    p.add_argument('--dst_login', help='nextgis.com folder id', type=str, required=True)
    p.add_argument('--dst_password', help='nextgis.com folder id', type=str, required=True)
    p.add_argument('--dst_group', help='nextgis.com folder id', type=int, required=True)



    return p.parse_args()

def get_ngw_layer_structure(ngw_url,layer_id,ngw_creds):

    url = ngw_url + '/api/resource/' +  str(layer_id)
    req = requests.get(url, auth=ngw_creds)

    return req.json()

def create_vector_layer(ngw_url,payload,ngw_creds, parent_id=0):
    url = ngw_url + '/api/resource/'

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(payload)

    req = requests.post(url, json = payload, auth=ngw_creds)

    print(req.content)

def prepare_structure(structure):

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
    '''
    del ns['resource']['id']
    del ns['resource']['creation_date']
    del ns['resource']['owner_user']
    del ns['resource']['children']
    del ns['resource']['interfaces']
    del ns['resource']['scopes']
    del ns['resource']['scopes']
    '''
    return ns

if __name__ == '__main__':

    args = get_args()

    src_creds = (args.src_login, args.src_password)
    dst_creds = (args.dst_login, args.dst_password)

    #get layer structure
    structure = get_ngw_layer_structure(args.src_url,args.src_layer, src_creds)


    structure['resource']['parent'] = {'id':args.dst_group}

    post_structure = prepare_structure(structure)

    #post layer structure
    create_vector_layer(args.dst_url,payload=post_structure,ngw_creds=dst_creds)
