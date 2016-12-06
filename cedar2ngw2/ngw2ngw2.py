#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Project: Two-directional synchrosnisation of 2 ngw layers for cead Project. 
# Author: Dmitry Baryshnikov <bishop.dev@gmail.com>
# Copyright: 2016, NextGIS <info@nextgis.com>

import json
import requests
import os
import config
from contextlib import closing
import pickle
import os.path

ngw1_url = config.ngw1_url
ngw1_id = config.ngw1_id
ngw1_creds = config.ngw1_creds

ngw2_url = config.ngw2_url
ngw2_id = config.ngw2_id
ngw2_creds = config.ngw2_creds

delta = 0.00000001

# ngw1 has priority over ngw2

def compareValues(value1, value2):
    if (value1 == '' or value1 == None) and (value2 == '' or value2 == None):
        return True

    if isinstance(value1, float) and isinstance(value2, float):
        return abs(value1 - value2) < delta

    if value1 != value2:
        return False
    return True

def compareFeatures(feature1, feature2):
    # Compare attributes
    fields1 = feature1['fields']
    fields2 = feature2['fields']
    for field in fields1:
        if not compareValues(fields1[field], fields2[field]):
            return False
    return True

def copyFeature(item, url_src, url_dst, feature_dst, creds_src, creds_dst):
    attachments = item['extensions']['attachment']

    #create new row
    item['extensions']['attachment'] = None
    req = requests.post(url_dst + feature_dst, data=json.dumps(item), auth=creds_dst)
    new_id = req.json()['id']
    #add attachements
    if attachments is not None:
        for attachment in attachments:
            attachment_id = attachment['id']

            with closing(requests.get(url_src + str(item['id']) + '/attachment/' + str(attachment_id) + '/download', auth=creds_src, stream=True)) as f:

                req = requests.put(url_dst + '/component/file_upload/upload', data=f, auth=creds_dst)
                json_data = req.json()
                json_data['name'] = attachment['name']

                attach_data = {}
                attach_data['file_upload'] = json_data

                req = requests.post(url_dst + feature_dst + str(new_id) + '/attachment/', data=json.dumps(attach_data), auth=creds_dst)
    return new_id


if __name__ == '__main__':

    ids_map = dict()
    if os.path.exists('ids.pkl'):
        pkl_file = open('ids.pkl', 'rb')
        ids_map = pickle.load(pkl_file)
        pkl_file.close()

    req = requests.get(ngw1_url + '/resource/'  + str(ngw1_id) + '/feature/', auth=ngw1_creds)
    dictionary1 = req.json()

    req = requests.get(ngw2_url + '/resource/'  + str(ngw2_id) + '/feature/', auth=ngw2_creds)
    dictionary2 = req.json()

    for item1 in dictionary1:
        id1 = item1['id']
        id1_exists = False
        if id1 in ids_map.keys():
            for item2 in dictionary2:
                if ids_map[id1] == item2['id']:
                    id1_exists = True
                    # Compare attributes
                    if not compareFeatures(item1, item2):
                        # Update feature2
                        print "Update feature " + str(id1)
                        req = requests.put(ngw2_url + '/resource/' + str(ngw2_id) + '/feature/' + str(ids_map[id1]), data=json.dumps(item1), auth=ngw2_creds)
                    break

        if id1_exists == False:
            # Copy id1 to ngw2
            print "Copy feature " + str(id1) + " to " + ngw2_url
            # def copyFeature(item, url_src, url_dst, feature_dst, creds_src, creds_dts):
            new_id = copyFeature(item1, ngw1_url + '/resource/' + str(ngw1_id) + '/feature/', ngw2_url, '/resource/' + str(ngw2_id) + '/feature/', ngw1_creds, ngw2_creds)
            ids_map[id1] = new_id

    for item2 in dictionary2:
        id2 = item2['id']
        id2_exists = False
        if id2 in ids_map.values():
            id2_exists = True

        if id2_exists == False:
            # Copy id2 to ngw1
            print "Copy feature " + str(id2) + " to " + ngw1_url
            new_id = copyFeature(item2, ngw2_url + '/resource/'  + str(ngw2_id) + '/feature/', ngw1_url, '/resource/' + str(ngw1_id) + '/feature/', ngw2_creds, ngw1_creds)
            ids_map[new_id] = id2

    output = open('ids.pkl', 'wb')
    pickle.dump(ids_map, output)
    output.close()

    print ids_map
