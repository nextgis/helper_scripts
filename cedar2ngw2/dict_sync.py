# -*- coding: utf-8 -*-
import json
import requests
import time
import config

from requests.auth import HTTPDigestAuth

dict_url = config.dict_url
dict_creds = config.dict_creds

ngw_url = config.ngw_url
ngw_creds = config.ngw_creds
timeout = config.timeout

dict_names = ('getTypeViolations', 'getProtectionForests', 'getSpecies', 'getStock', 'getHeight', 'getStatus' )
#dict_names = ('getTypeViolations', 'getStock', 'getHeight', 'getStatus' )

ngw_resources = (40, 41, 45, 46, 59, 74)
#ngw_resources = (40, 46, 59, 74)

if __name__ == '__main__':

    for resid, name in (zip(ngw_resources, dict_names)):
	print "sync " + name + " ..."
	try:
	    s = requests.session()
    	    req = s.get(dict_url + name, auth=HTTPDigestAuth(*dict_creds))
    	    dictionary = req.json()

    	    items = {}
    	    for item in dictionary:
        	elem = item.get('name')
		if isinstance(elem, int):
		    elem = str(elem)
        	items[elem] = elem
	
	    payload = {'lookup_table': {'items': items}}
	    t = requests.session()
    	    req = t.put(ngw_url + str(resid), data=json.dumps(payload), auth=ngw_creds)

	except requests.exceptions.RequestException as e:
	    print 'requests error ', resid, e, ' sleep 5 sec.'
	    time.sleep(timeout)