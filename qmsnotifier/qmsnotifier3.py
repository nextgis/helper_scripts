#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
#
# qmsnotifier.py
# ---------------------------------------------------------
# Send notifications about new QMS services to Telegram channel through a bot (Python 3 version)
# More: http://github.com/nextgis/helper_scripts/qmsnotifier
#
# Usage: 
#      qmsnotifier.py [-h]
#      where:
#           -h              show this help message and exit
# Example:
#      python qmsnotifier.py
#
# Copyright (C) 2017-present Maxim Dubinin (maxim.dubinin@nextgis.com)
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

import requests
import argparse
import json
import os
import sys
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('-t','--testmode', action="store_true", help='Run in test mode')
args = parser.parse_args()

#################BOT TOKEN##################
token = open('token').read().rstrip('\n')
tele = open('tele').read().rstrip('\n')
#################BOT TOKEN##################

method = 'sendMessage'
chat_id = -1001104876475 #@qmsupdates
test_chat_id = -1001084564203 #@nextgis_chat
if args.testmode: chat_id = test_chat_id

def downloadqms():
    url='https://qms.nextgis.com/api/v1/geoservices/?format=json'
    filename='qms.json'
    r = requests.get(url)
    with open(filename, "wb") as data_file:
        data_file.write(r.content)

    with open(filename) as data_file:    
        qmslist_new = json.load(data_file)
        
    return qmslist_new

def find_qms(id):
    #   Search in qms for layer
    exist_qms = False
    for qmslayer in qmslist_old:
        if id == qmslayer['id']:
                exist_qms = True

    return exist_qms

def get_url(id):
    #Get URL for which service is created, needs separate request
    response = requests.post(url='http://qms.nextgis.com/api/v1/geoservices/' + id)
    return response.json()['url']

def get_name(guid):
    userpage = requests.get('https://my.nextgis.com/public_profile/' + guid)
    soup = BeautifulSoup(userpage.content, 'html.parser')
    divs = soup.findAll("div", { "class" : "form-group label-floating clearfix" })
    username = divs[0].next_element.next_element.next_element.next_element.strip(' ').strip('\n').strip(' ')
    
    return username
    
def notify(type,link,name,url,submitter):
    text = u'New %s QMS service %s\nName: %s\nSubmitter: %s\nUrl: %s' % (type,link,name,submitter,url)
    
    session = requests.session()
    session.proxies = {'https':  tele}
                   
    response = session.post(
        url='https://api.telegram.org/bot{0}/{1}'.format(token, method),
        data={'chat_id': chat_id, 'text': text}
    ).json()
    print(response)
    
if __name__ == '__main__':
    if os.path.exists("qms_old.json"): os.remove("qms_old.json")

    if os.path.exists("qms.json"):
        os.rename("qms.json","qms_old.json")

        qmslist_new = downloadqms()
        
        with open("qms_old.json") as data_file:    
            qmslist_old = json.load(data_file)
        
        for item in qmslist_new:
            exist_qms = find_qms(item['id'])
            if exist_qms == False:
                #print('id' + str(item['id']))
                type = item['type'].upper()
                link = 'https://qms.nextgis.com/geoservices/' + str(item['id'])
                name = item['name']
                url = get_url(str(item['id']))
                submitter = get_name(item['submitter'])
                notify(type,link,name,url,submitter)
    else:
        notify('type','link','name','Something went wrong, qms.json is missing','submitter')