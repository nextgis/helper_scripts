#!/usr/bin/env python
# -*- coding: utf-8 -*-
#******************************************************************************
#
# photos2ngw.py
# ---------------------------------------------------------
# Upload images to a Web GIS
# More: https://gitlab.com/nextgis/helper_scripts
#
# Usage:
#      photos2ngw.py [-h] [-o] [-of ORIGINALS_FOLDER]
#      where:
#           -h              show this help message and exit
#           -o              overwrite
#           -of             relative path to folder with originals
#           -t              type of data, license or gin
# Example:
#      python photos2ngw.py -of originals_gkm -t gkm
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

import os, sys
import requests
import json
import urllib2
from contextlib import closing

try:
    import config
except ImportError:
    print "config.py not found. Copy config.example.py to config.py, and set your Web GIS credentials here. See readme.md"
    quit()

def get_args():
    p = argparse.ArgumentParser(description="Replicate vector layer from ngw to other ngw")
    p.add_argument('--debug', '-d', help='debug mode', action='store_true')
    return p.parse_args()



'''
Simple master-slave replication

Layers should have same fields
'''

class Replicator():

    debug = True

    def check_layers_has_same_structure(self):

        return True
    def truncate_secondary_layer(self, ngw_url, layer_id, ngw_creds):
        req = requests.delete(ngw_url + '/api/resource/' + str(layer_id) + '/feature/', auth=ngw_creds)

    def get_ngw_layer_dump(self,ngw_url,layer_id,ngw_creds):
        try:
            url = ngw_url + '/api/resource/' +  str(layer_id) + '/feature/'
            if self.debug:
                print url
            req = requests.get(url,  auth=ngw_creds)
            req.raise_for_status()

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)

        return req.json()

    def dump_rest_prepare(self,source_dump):
        #take ngw vector layer dump (list)
        #delete attachment and id fields


        dump = list()
        new_dump = list()
        for feature in source_dump:
            dump.append(feature)


        for element in dump:
            new_element = element

            if 'attachment' in new_element['extensions']: del new_element['extensions']['attachment']
            if 'description' in new_element['extensions']: del new_element['extensions']['description']
            if 'id' in new_element: del new_element['id']
            new_dump.append(new_element)
        return new_dump

    def create_vector_features(self,layer_id,ngw_url,ngw_creds,dump):
        features_count = len(dump)
        step = 50
        i=0
        while i < features_count:
            block = list()
            block = dump[i:i+step]
            url = ngw_url + '/api/resource/' + str(layer_id) + '/feature/'
            if self.debug:
                print 'perform patch query'
                print url
            try:
                #more smart requests call for easer debug
                req = requests.Request('PATCH',url ,data=json.dumps(block), auth=ngw_creds)
                prepared = req.prepare()
                def pretty_print_query(req):
                    print('\n{}\n{}\n{}\n\n{}'.format(
                        '-----------REQUEST-----------',
                        req.method + ' ' + req.url,
                        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
                        req.body,
                    ))

                pretty_print_query(prepared)
                s = requests.Session()
                s.send(prepared)

                #req.raise_for_status()

            #error handling for query
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                print e
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                sys.exit(1)


            i = i + step
        if self.debug:
            print 'vector features creation completed'

    def get_match_feature_id_by_order(self,object_number,dump):
        match_object = dump[object_number]
        return match_object['id']

    def feature_has_atachments(self,feature):
        print feature
        if feature['extensions']['attachment'] is None:
            return False
        else:
            return True

    def replicate_attachments(self, primary_ngw_url, primary_layer_id, primary_ngw_creds, secondary_ngw_url, secondary_layer_id, secondary_ngw_creds, dump):


        features_count = len(dump)
        dump_secondary = self.get_ngw_layer_dump(ngw_url = secondary_ngw_url,layer_id = secondary_layer_id,ngw_creds = secondary_ngw_creds)
        i=0
        while i < features_count:
            feature_primary = dump[i]
            if self.debug:
                print i
            if self.feature_has_atachments(feature_primary):
                if self.debug: print 'feature has attachments'

                #secondary_layer_feature_id = self.get_match_feature_id_by_order(object_number=i,dump = dump_secondary)
                #secondary_feature_id = dump_secondary[i]['id']
                #now feature in secondary layer do not have attachments
                #копирование атачментов из фичи одного слоя в фичу другого
                for attachment in feature_primary['extensions']['attachment']:
                    if self.debug: print  'upload attachment ' + attachment['name']
                    #here will be creds of primary layer
                    #todo скачивание аттачментов с паролем
                    attachment_url=primary_ngw_url + '/api/resource/' + primary_layer_id + '/feature/' + str(feature_primary['id']) + '/attachment/' + str(attachment['id']) + '/download'
                    if self.debug: print 'get attachment url: ', attachment_url
                    #Get file from internet, optionally with auth
                    with closing(requests.get(attachment_url, auth=primary_ngw_creds, stream=True)) as f:

                        #upload attachment to nextgisweb
                        secondary_feature_id = dump_secondary[i]['id']
                        url = secondary_ngw_url + '/api/component/file_upload/upload'
                        req = requests.put(url, data=f, auth=secondary_ngw_creds)

                        #print req.content
                        json_data = req.json()
                        json_data['name'] = attachment['name']

                        attach_data = {}
                        attach_data['file_upload'] = json_data

                        #add attachment to nextgisweb feature

                        url = secondary_ngw_url + '/api/' + '/resource/' + secondary_layer_id + '/feature/'+  str(secondary_feature_id) + '/attachment/'
                        req = requests.post(url, data=json.dumps(attach_data), auth=secondary_ngw_creds)


                    '''
                    headers = {'Content-type': 'application/x-www-form-urlencoded'}
                    payload={'file':urllib2.urlopen(attachment_url),'name':attachment['name']}

                    #here will be creds of secondary layer

                    url = secondary_ngw_url + '/api/component/file_upload/upload'
                    if self.debug: print  'Upload attachment to ' + url
                    req = requests.post(url,  data=payload, auth=secondary_ngw_creds, headers=headers)

                    print req

                    json_data = req.json()
                    attach_data = {}
                    attach_data['file_upload'] = json_data

                    if self.debug: print  'Грузим атачмент'
                    secondary_feature_id = dump_secondary[i]['id']
                    url = secondary_ngw_url + '/api/' + '/resource/' + secondary_layer_id + '/feature/'+  str(secondary_feature_id) + '/attachment/'
                    if self.debug: print url
                    req = requests.post(url,  data=json.dumps(attach_data), auth=secondary_ngw_creds, headers=headers)
                    '''
            i=i+1





#я сломал голову, поэтому разбил всё на кучу методов



replicator = Replicator()

#Check if both layers has same fields
replicator.check_layers_has_same_structure()

#Check if both layers are equal using ngw_id as order
#Check if all attachments are equal using ngw_id as order
#If both of last check true - replication not needed

#Truncate secondary layer
replicator.truncate_secondary_layer(ngw_url=config.secondary_ngw_url, layer_id = config.secondary_ngw_layer_id, ngw_creds = config.secondary_ngw_creds)
#Get primary layer as JSON dump
primary_layer_dump = replicator.get_ngw_layer_dump(ngw_url=config.primary_ngw_url, layer_id = config.primary_ngw_layer_id, ngw_creds = config.primary_ngw_creds)


#Prepare dump for features create (drop attachments records)
primary_layer_dump_rest_prepared = replicator.dump_rest_prepare(primary_layer_dump)

#Create features from dump using PATCH query
result = replicator.create_vector_features(ngw_url=config.secondary_ngw_url, layer_id = config.secondary_ngw_layer_id, ngw_creds = config.secondary_ngw_creds,dump = primary_layer_dump_rest_prepared)


primary_layer_dump = replicator.get_ngw_layer_dump(ngw_url=config.primary_ngw_url, layer_id = config.primary_ngw_layer_id, ngw_creds = config.primary_ngw_creds)
#проблемы с передачей кортежа по значению/по ссылке, поэтому запрашиваю второй раз

#Upload attachments
result = replicator.replicate_attachments(primary_ngw_url=config.primary_ngw_url, primary_layer_id = config.primary_ngw_layer_id, primary_ngw_creds = config.primary_ngw_creds,
secondary_ngw_url=config.secondary_ngw_url, secondary_layer_id = config.secondary_ngw_layer_id, secondary_ngw_creds = config.secondary_ngw_creds, dump = primary_layer_dump)
