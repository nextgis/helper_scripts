#!/usr/bin/env python

'''
Usage:
   python bbox2csv.py > bounds.csv   
'''
from bs4 import BeautifulSoup
import requests 
import sys

def get_bboxes(guid):
    url = link2.replace('GUID',guid)
    bboxes = ''
    json = requests.get(url).json()
    if json['data'] != None:
        bboxes = json['data']['ngwcluster']['bboxes']
    return bboxes

def bbox2wkt(minx, miny, maxx, maxy):
    # first validate bbox values
    assert isinstance(minx,float) or isinstance(minx,int)
    assert isinstance(miny,float) or isinstance(miny,int)
    assert isinstance(maxx,float) or isinstance(maxx,int)
    assert isinstance(maxy,float) or isinstance(maxy,int)
    assert (minx <= maxx), 'failed: %s is not <= %s' % (minx,maxx)
    assert (miny <= maxy), 'failed: %s is not <= %s' % (miny,maxy)
    return "Polygon((%(minx)s %(miny)s, %(minx)s %(maxy)s, %(maxx)s %(maxy)s, %(maxx)s %(miny)s, %(minx)s %(miny)s))" % locals()

if __name__ == "__main__":
    #################SECRET LINKS##########################
    link1 = open('sensitive').read().rstrip('\n').split(',')[0]
    link2 = open('sensitive').read().rstrip('\n').split(',')[1]
    #################SECRET LINKS##########################
    print 'url,wkt,url'

    allinsts = requests.get(link1)
    soup = BeautifulSoup(allinsts.content, 'html.parser')
    trs = soup.findAll('tr')
    for i in xrange(1,len(trs)):
        tds = trs[i].findAll('td')
        #if tds[3].text.strip('\n') == 'lemon':
        guid = tds[1].text.strip('\n')
        url = 'http://' + tds[4].text.strip('\n')
        #b 44, 'maxim' in url //conditional break
        sys.stderr.write(url + '\n')
        bboxes = get_bboxes(guid)

        if bboxes != '':
            for bbox in bboxes:
                print '"%s","%s","%s"' % (bbox2wkt(*map(float,bbox)),'bounds', url)