#!/usr/bin/python
# Update qms service boundary
# Example: python update_bbox.py --user admin_qms --passw *** --sid 999 --bfile geoms/999.wkt
#          python update_bbox.py --user admin_qms --passw *** --sid 635 --bstr "SRID=4326;MULTIPOLYGON (((-8.8769531237642880 -10.1419316847338870, 13.9746093730550811 -10.1419316847338870, 13.9746093730550811 11.8673509098307584, -8.8769531237642880 11.8673509098307584, -8.8769531237642880 -10.1419316847338870)))"

import argparse
import requests

QMS_URL = 'https://qms.nextgis.com/api/vX/geoservices/'

# 0. Get args
argparser = argparse.ArgumentParser()
argparser.add_argument('--user', type=str, help='Username', required=True)
argparser.add_argument('--passw', type=str, help='Password', required=True)
argparser.add_argument('--sid', type=int, help='Service ID')
argparser.add_argument('--bfile', type=str, help='File with new boundary (WKT)')
argparser.add_argument('--bstr', type=str, help='New boundary as WKT string')
argparser.add_argument('--list', action='store_true', help='Show services id')

args = argparser.parse_args()

# 1. Login
session = requests.session()
session.auth = (args.user, args.passw)
service_list_resp = session.get(QMS_URL)
assert service_list_resp.status_code<400

# 2. If List services - simple show
if args.list:
    services = service_list_resp.json()['results']
    for service in services:
        print(u'{0: <5} {1}'.format(service['id'], service['name']))
    exit()

# 3. Set new boundary
assert args.sid != None
assert (args.bfile !=None or args.bstr!= None)

boundary_str = args.bstr
if args.bfile:
    with open(args.bfile) as f:
        boundary_str = f.read()

payload = {'boundary': boundary_str}
resp = session.patch(QMS_URL + str(args.sid) + '/', data=payload)
assert resp.status_code < 400







