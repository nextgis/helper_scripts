#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import argparse
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from datetime import datetime
import string

valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

#python ngw_countattachments.py --url demo.nextgis.ru --login test --password testtest --layer_id 6209

parser = argparse.ArgumentParser()
parser.add_argument('--url',type=str,required=True)
parser.add_argument('--login',type=str,default='administrator')
parser.add_argument('--password',type=str)
parser.add_argument('--layer_id',type=str,required=True)

args = parser.parse_args()

def get_data(url, login, password, layer_id):
    if args.login and args.password:
        AUTH = HTTPBasicAuth(login, password)
    else:
        AUTH = ''
    resource_url = 'https://%s/api/resource/%s' %(url, layer_id)
    resource = requests.get(resource_url, auth = AUTH).json()
    
    if 'exception' not in resource.keys():
        if resource['resource']['cls'] == 'vector_layer' or resource['resource']['cls'] == 'postgis_layer':
            print ('Downloading structure...')
            data = requests.get(resource_url + '/geojson', auth = AUTH).json()

            features = requests.get(resource_url + '/feature/', auth = AUTH).json()

            i = 0
            pbar = tqdm(total=len(features))
            for elem in features:
                if elem["extensions"]["attachment"] != None:
                    attach_count = len(elem["extensions"]["attachment"])
                else:
                    attach_count = 0
                
                #add field and value
                data['features'][i]['properties']['attach_count'] = attach_count
                i = i + 1
                pbar.update(1)
            pbar.close()

            with open('data.json', 'w') as f:
                json.dump(data, f)    

        else:
            print('Resource %s is not a vector layer' % layer_id)
    else:
        print('Resource %s does not exist' % layer_id)
        
if __name__ == '__main__':
    
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")

    get_data(args.url, args.login, args.password, args.layer_id)

