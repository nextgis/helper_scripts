# -*- coding: utf-8 -*-
import json
import requests
import time

from requests.auth import HTTPDigestAuth


dict_url = 'http://0.0.0.0/'
dict_creds = ('source_login', 'source_password')
dict_names = ('source_dict_name1', 'source_dict_name2', 'source_dict_name2' )

ngw_url = 'http://1.1.1.1'
ngw_creds = ('ngw_login', 'ngw_password')
ngw_resources = (40, 41, 42)

if __name__ == '__main__':

    for resid, name in (zip(ngw_resources, dict_names)):
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
	    time.sleep(5)

