#Outputs a list of ids of resources for which permissions are set
#python ngw_check_permissions.py -u sandbox -r https -n administrator -p demodemo

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

for item in items:
    if item['resource']['permissions'] != []:
        print(item['resource']['id'])