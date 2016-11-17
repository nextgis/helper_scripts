# -*- coding: utf-8 -*-
import json
import requests
import pprint
import math
import os
import config

from datetime import datetime, date, time
from requests.auth import HTTPDigestAuth
from dateutil.parser import parse

# new API citorus
# http://91.239.143.154/cedar/updateObj?begin=1990-01-01T00:00:00.000Z&end=2015-09-21T00:00:00.000Z
# http://91.239.143.154/cedar/updateObj?begin="1990-12-31T00:00:00.000Z"&end="2015-08-18T00:00:00.000Z"
# response: {"objectID":"A4754895o21052o63814o14197o799578","number":3266,"source":"Веб-GIS","sourceID":13767,"applicant":"","controller":"","region":{"key":"","value":"Приморский край"},"district":"","city":"","landmarks":"","forestery":"Рощинское","precinct":"Таежное","territory":[{"vydel":46}],"geo":[136.404910714,46.008964285699925],"violations":[],"description":"","species":"","date":"2015-09-18T00:00:00.000Z","time":"00:00","area":"","status":"Новое лесоизменение"}
# http://176.9.38.120/fv/api/resource/57?objectID=A4754895o21052o63814o14197o799578
# last cedar API
# http://91.239.143.154/cedar/updateObj?begin=2015-10-10T00:00:00.000Z&end=2015-10-20T00:00:00.000Z

dict_url = config.dict_url
dict_creds = config.dict_creds

ngw_url = config.ngw_url
ngw_creds = config.ngw_creds
timeout = config.timeout

earthRadius = 6378137.0

def wgs84ToMercatorSphereX(x):
    print 'x: ', x
    return earthRadius * math.radians(x)
    
def wgs84ToMercatorSphereY(y):
    print 'y ', y
    return earthRadius * math.log(math.tan(math.pi / 4 + math.radians(y) / 2))
    
def parseGeom(geodict):
    firstVal = geodict[0]

    if firstVal is None:
	return None

    if type(firstVal) is float:
	if geodict[0] > 180 or geodict[0] < -180 or geodict[1] > 90 or geodict[1] < -90:
	    return None
        geom = 'MULTIPOINT ('
        geom += str(wgs84ToMercatorSphereX(geodict[0]))
        geom += u' '
        geom += str(wgs84ToMercatorSphereY(geodict[1]))
        geom += ')'
        return geom
    elif type(firstVal) is int:
	dx = float(geodict[0])
	dy = float(geodict[1])
	if dx > 180 or dx < -180 or dy > 90 or dy < -90:
    	    return None
        geom = 'MULTIPOINT ('
        geom += str(wgs84ToMercatorSphereX(dx))
        geom += u' '
        geom += str(wgs84ToMercatorSphereY(dy))
        geom += ')'
        return geom
    else:
        geom = 'MULTIPOINT ('
        geosubdict = firstVal        
        for geoitem in geosubdict:
	   if type(geoitem[0]) is not float:
		return None
           if geom != 'MULTIPOINT (':
               geom += ', '
           geom += str(wgs84ToMercatorSphereX(geoitem[0]))
           geom += u' '
           geom += str(wgs84ToMercatorSphereY(geoitem[1]))
        geom += ')'
        return geom 
        
def getFeatureIdforObjectId(objectId):
    req = requests.get(ngw_url + '57/feature/?objectID=' + objectId, auth=ngw_creds)     
    dictionary = req.json()  
    for item in dictionary:
        return item.get('id')
    return None    
    

if __name__ == '__main__':

    # read last script run timestamp
    if os.path.isfile('last_update'):
        with open('last_update', 'r') as f:
           lastDtStr = f.read()
    # or set it to default value
    else:
        lastDtStr = "1990-01-01T00:00:00.000Z"
    
    nowDtStr = datetime.now().isoformat() + 'Z';
    
    lastDt = parse(lastDtStr)    
    nowDt = parse(nowDtStr)
    
    if lastDt.year == nowDt.year and lastDt.month == nowDt.month and lastDt.day == nowDt.day:
        print 'already worked today! let me relax please!'
        exit()
    
    srsUrl = dict_url + 'updateObj' + '?begin=' + lastDtStr + '&end=' + nowDtStr
    print srsUrl
    
    req = requests.get(srsUrl, auth=HTTPDigestAuth(*dict_creds))
    dictionary = req.json()
        
    # pp = pprint.PrettyPrinter(indent=4)
        
    for item in dictionary:
        #pp.pprint(item)
                
        # check if update or insert
        objectId = item.get('objectID')
        ngwFeatureId = getFeatureIdforObjectId(objectId)
        
        if item.get('geo') is None:
            continue            

        geom = parseGeom(item.get('geo'))
	if geom is None:
	    continue

        #parse date
        datestring = item.get('date')
        if datestring is None:
            year = 1970
            month = 1
            day = 1
            hour = 0
            minute = 0
            second = 0
        else:
            date = parse(datestring)
            timestring = item.get('time')
            timedict = timestring.split(':')
            year = date.year
            month = date.month
            day = date.day
            hour = int(timedict[0])
            minute = int(timedict[1])
            second = 0
                      
        territoryStr = u''
        for teritem in item.get('territory'):
            quarter = teritem.get('quarter')
            if quarter is not None and quarter != '':
		try:
            	    territoryStr += u'квартал ' + str(quarter)
		except:
		    pass

            vydel = teritem.get('vydel')
            if vydel is not None:
                try:
		    territoryStr += u' выдел ' + str(vydel)
		except:
		    pass

        # print  territoryStr
        # "region":{"key":"","value":"Приморский край"}
        
        region = item.get('region')
        regionStr = region.get('value')

        # print regionStr

        nnumber = 0
        if item.get('number') != '':
            nnumber = int(item.get('number'))
               
        payload = {
            'geom': geom,
            'fields':
                {
                'applicant': item.get('applicant'),
                'area': item.get('area'),
                'city': item.get('city'),
                'controller': item.get('controller'),
                'description': item.get('description'),
                'district': item.get('district'),
                'forestery': item.get('forestery'),
                'landmarks': item.get('landmarks'),
                'number': nnumber,
                'objectID': objectId,
                'precinct': item.get('precinct'),
                'protection': item.get('protection'),
                'region': regionStr,
                'source_': item.get('source'),
                'sourceID': item.get('sourceID'),
                'species': item.get('species'),
                'status': item.get('status'),
                'territory': territoryStr,
                'date' : {
                    'year' : year,
                    'month' : month,
                    'day' : day,
                    'hour' : hour,
                    'minute' : minute,
                    'second' : second }
                }
            }

        print payload
        if ngwFeatureId is None:
            print 'object id ' + objectId + ' -- insert new feature'
            req = requests.post(ngw_url + '57/feature/', data=json.dumps(payload), auth=ngw_creds)
        else:
            req = requests.put(ngw_url + '57/feature/' + str(ngwFeatureId), data=json.dumps(payload), auth=ngw_creds)
            print 'object id ' + objectId + ' -- update feature #' + str(ngwFeatureId)

        #print req
        #print req.json()

    # save last run time
    with open('last_update', 'w') as f:
        f.write(datetime.now().isoformat() + 'Z')
