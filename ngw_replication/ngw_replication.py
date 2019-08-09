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
import argparse
from copy import deepcopy
from contextlib import closing
import datetime


def get_args():
    epilog = '''Sample: '''
    epilog +=  '''
    python ngw_replication.py -url1 "http://dev.nextgis.com/sandbox" -layer1 247 -login1 administrator -pass1 demodemo -url2 "http://dev.nextgis.com/sandbox" -layer2 491 -login2 administrator -pass2 demodemo '''
    epilog +=  '''
    This script erases metadata of layer'''
    p = argparse.ArgumentParser(description="Replicate vector layer from ngw to other ngw", epilog=epilog)

    p.add_argument('--primary_ngw_url','-url1',required=True)
    p.add_argument('--primary_ngw_layer','-layer1',required=True)
    p.add_argument('--primary_ngw_login','-login1',required=True)
    p.add_argument('--primary_ngw_password','-pass1',required=True)

    p.add_argument('--secondary_ngw_url','-url2',required=True)
    p.add_argument('--secondary_ngw_layer','-layer2',required=True)
    p.add_argument('--secondary_ngw_login','-login2',required=True)
    p.add_argument('--secondary_ngw_password','-pass2',required=True)

    p.add_argument('--debug', '-d', help='debug mode', action='store_true')
    #p.add_argument('--config', help='patch to config.py file',required=False)
    return p.parse_args()

# --------------- config read ---------------
args = get_args()

class Config():
    #same interface like "import config"

    def __init__(self,url1,layer1,login1,pass1,url2,layer2,login2,password2):
        self.primary_ngw_url = url1
        self.primary_ngw_layer_id = layer1
        self.primary_ngw_creds = (login1,pass1)
        #self.primary_ngw_password = pass1

        self.secondary_ngw_url = url2
        self.secondary_ngw_layer_id = layer2
        self.secondary_ngw_creds = (login2,password2)
        #self.secondary_ngw_password = password2





config = Config(args.primary_ngw_url,args.primary_ngw_layer,args.primary_ngw_login,args.primary_ngw_password,args.secondary_ngw_url,args.secondary_ngw_layer, args.secondary_ngw_login,args.secondary_ngw_password)


'''
# import config from program argument
try:
    import imp
    config = imp.load_source('config', args.config)

except:
    path = os.path.abspath(args.config)
    print "config.py not found at {path} Copy config.example.py to config.py, and set your Web GIS credentials here. See readme.md".format(path=path)
    quit()
'''


'''
Simple master-slave replication

Layers should have same fields
'''

class Replicator():

    debug = args.debug

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
        #this list can be used in POST/PATCH query, and using for compare features


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

                if self.debug:
                    self.pretty_print_query(prepared)
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
    def is_layers_features_equal(self, primary_ngw_url, primary_ngw_layer_id, primary_ngw_creds, secondary_ngw_url, secondary_ngw_layer_id, secondary_ngw_creds):
        primary_layer_dump = self.get_ngw_layer_dump(ngw_url=primary_ngw_url, layer_id = primary_ngw_layer_id, ngw_creds = primary_ngw_creds)
        secondary_layer_dump = self.get_ngw_layer_dump(ngw_url=secondary_ngw_url, layer_id = secondary_ngw_layer_id, ngw_creds = secondary_ngw_creds)

        cp1=deepcopy(primary_layer_dump)
        cp2=deepcopy(secondary_layer_dump)
        primary_dump_shaved = self.dump_rest_prepare(cp1)
        secondary_dump_shaved = self.dump_rest_prepare(cp2)


        equal = primary_dump_shaved == secondary_dump_shaved
        #да, такой способ репликации, при котором все фичи грохаются и грузятся сразу все, позволяет сравнивать слои вот таким образом.
        #в худшем случае могут быть ложно-положительные срабатывания, но эт ничего

        primary_layer_dump = self.get_ngw_layer_dump(ngw_url=primary_ngw_url, layer_id = primary_ngw_layer_id, ngw_creds = primary_ngw_creds)
        secondary_layer_dump = self.get_ngw_layer_dump(ngw_url=secondary_ngw_url, layer_id = secondary_ngw_layer_id, ngw_creds = secondary_ngw_creds)

        if equal:
            atachments_equal = self.is_atachments_equal(deepcopy(primary_layer_dump),deepcopy(secondary_layer_dump))
            if atachments_equal == False:
                return False
            else:
                return True

    def is_atachments_equal(self,primary_layer_dump,secondary_layer_dump):
        #take two full layer dumps
        #assume that both dumps have same features count (already checked before)
        #return true when attachments have same size and filename

        if self.debug: print 'check is_atachments_equal'
        i = 0
        cnt = len(primary_layer_dump)
        for feature in primary_layer_dump:

            primary_attachments = primary_layer_dump[i]['extensions']['attachment']
            secondary_attachments = secondary_layer_dump[i]['extensions']['attachment']
            if (primary_attachments is None and secondary_attachments is None): #both features without attachments
                i=i+1
                continue
            if (primary_attachments is None and secondary_attachments is not None): #one layer have attachments, other not have
                return False
            if (primary_attachments is not None and secondary_attachments is None): #one layer have attachments, other not have
                return False
            if len(primary_attachments) != len(secondary_attachments):
                if self.debug: print 'feature {id} unmatch attachments count'.format(id=primary_layer_dump[i]['id'])
                return False

            #if attachment has deleted and changed to other file
            attachment_number = 0
            while attachment_number < len(primary_attachments):
                if primary_attachments[attachment_number]['name'] != secondary_attachments[attachment_number]['name']: return False
                if primary_attachments[attachment_number]['size'] != secondary_attachments[attachment_number]['size']: return False
                if primary_attachments[attachment_number]['mime_type'] != secondary_attachments[attachment_number]['mime_type']: return False
                if primary_attachments[attachment_number]['description'] != secondary_attachments[attachment_number]['description']: return False
                attachment_number = attachment_number + 1

            i=i+1

        return True

    def is_layers_featurecount_equal(self, primary_ngw_url, primary_layer_id, primary_ngw_creds, secondary_ngw_url, secondary_layer_id, secondary_ngw_creds):
        #return true if both layers have same features count
        try:
            url = primary_ngw_url + '/api/resource/' +  str(primary_layer_id) + '/feature_count'
            if self.debug:
                print url
            req = requests.get(url,  auth=primary_ngw_creds)
            req.raise_for_status()

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)

        primary_layer_json = req.json()
        cnt1 = int(primary_layer_json['total_count'])

        try:
            url = secondary_ngw_url + '/api/resource/' +  str(secondary_layer_id) + '/feature_count'
            if self.debug:
                print url
            req = requests.get(url,  auth=secondary_ngw_creds)
            req.raise_for_status()

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit(1)

        secondary_layer_json = req.json()
        cnt2 = int(secondary_layer_json['total_count'])


        if cnt1 == cnt2:
            return True
        else:
            return False

    def pretty_print_query(self,req):
        print('\n{}\n{}\n{}\n\n{}'.format(
            '-----------REQUEST-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))



    def add_metadata(self, ngw_url, layer_id, ngw_creds,key,value):
        payload = dict()
        payload['resmeta'] = dict()
        payload['resmeta']['items'] = dict()
        payload['resmeta']['items'][key] = value

        url = ngw_url + '/api/resource/' + layer_id
        #more smart requests call for easer debug
        req = requests.Request('PUT',url ,data=json.dumps(payload), auth=ngw_creds)
        prepared = req.prepare()

        if self.debug:
            self.pretty_print_query(prepared)
        s = requests.Session()
        s.send(prepared)

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
                        req = requests.put(url, data=f.content, auth=secondary_ngw_creds)

                        #print req.content
                        json_data = req.json()
                        json_data['name'] = attachment['name']

                        attach_data = {}
                        attach_data['file_upload'] = json_data

                        #add attachment to nextgisweb feature

                        url = secondary_ngw_url + '/api/resource/' + secondary_layer_id + '/feature/'+  str(secondary_feature_id) + '/attachment/'
                        #req = requests.post(url, data=json.dumps(attach_data), auth=secondary_ngw_creds)
                        req = requests.Request('POST',url=url ,data=json.dumps(attach_data), auth=secondary_ngw_creds)
                        prepared = req.prepare()

                        if self.debug:  self.pretty_print_query(prepared)
                        s = requests.Session()
                        s.send(prepared)


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

# ------ check if anything different in layers -----------
feature_count_equal = False
all_features_equal = False

feature_count_equal = replicator.is_layers_featurecount_equal(primary_ngw_url=config.primary_ngw_url, primary_layer_id = config.primary_ngw_layer_id, primary_ngw_creds = config.primary_ngw_creds,
secondary_ngw_url=config.secondary_ngw_url, secondary_layer_id = config.secondary_ngw_layer_id, secondary_ngw_creds = config.secondary_ngw_creds)

if feature_count_equal:
    all_features_equal = replicator.is_layers_features_equal(primary_ngw_url=config.primary_ngw_url, primary_ngw_layer_id = config.primary_ngw_layer_id, primary_ngw_creds = config.primary_ngw_creds,
    secondary_ngw_url=config.secondary_ngw_url, secondary_ngw_layer_id = config.secondary_ngw_layer_id, secondary_ngw_creds = config.secondary_ngw_creds)

#print update time in metadata, for control
result = replicator.add_metadata(ngw_url=config.secondary_ngw_url, layer_id = config.secondary_ngw_layer_id, ngw_creds = config.secondary_ngw_creds,key='CHECKED_AT',value=str(datetime.datetime.now()))
if all_features_equal:
    quit('all features equal')
# ------ check if anything different in layers -----------



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

#print update time in metadata, for control
result = replicator.add_metadata(ngw_url=config.secondary_ngw_url, layer_id = config.secondary_ngw_layer_id, ngw_creds = config.secondary_ngw_creds,key='UPDATED_AT',value=str(datetime.datetime.now()))
