#!/usr/bin/env python

'''
Usage:
   python inst_webmaps2csv.py > webmaps.csv
'''
from bs4 import BeautifulSoup
import requests 
import sys

def get_webmaps(guid):
    url = link2.replace('GUID',guid)
    webmaps = ''
    numlayers = 0
    json = requests.get(url, auth=('', password)).json()
    if json['data'] != None and 'layer' in json['data']['webmap']['item_type'].keys():
        webmaps = json['data']['ngwcluster']['webmaps']
        numlayers = json['data']['webmap']['item_type']['layer']
    return numlayers,webmaps

if __name__ == "__main__":
    #################SECRET LINKS##########################
    link1 = open('sensitive').read().rstrip('\n').split(',')[0]
    link2 = open('sensitive').read().rstrip('\n').split(',')[1]
    password = open('sensitive').read().rstrip('\n').split(',')[2]
    #################SECRET LINKS##########################
    print 'base_url,num_layers,webmap_id,webmap_link'

    allinsts = requests.get(link1, auth=('', password))
    soup = BeautifulSoup(allinsts.content, 'html.parser')
    trs = soup.findAll('tr')
    for i in xrange(1,len(trs)):
        tds = trs[i].findAll('td')
        #if tds[3].text.strip('\n') == 'lemon':
        guid = tds[1].text.strip('\n')
        url = 'http://' + tds[4].text.strip('\n')
        #b 44, 'maxim' in url //conditional break
        sys.stderr.write(url + '\n')
        numlayers,webmaps = get_webmaps(guid)

        if webmaps != '':
            for webmap in webmaps:
                webmap_link = url + '/resource/' + str(webmap) + '/display'
                print '%s,%s,%s,%s' % (url,numlayers,webmap,webmap_link)