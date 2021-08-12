#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import dateutil
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
                               
import datetime

import csv

#csvfile='STATISTICS/20210809_161645.csv'
csvfile='STATISTICS/merged.csv'
with open(csvfile, newline='') as f:
    reader = csv.DictReader(f)
    data = list(reader)
    
    

n = 1024

x_values = [10,100,200,300]
y_values = [10,90,180,250]

#plt.plot(x_values, y_values, linestyle='--', marker='o', color='b')

fig, ax = plt.subplots()
plt.xticks(())
plt.yticks(())


xys=list()
for element in data:
    if element['mode']=='1':
        xys.append([int(element['features']),int(element['duration'])])

if len(xys) > 0:
    x, y = zip(*xys)
    plt.scatter(x,y)
    plt.plot(x,y, '-o')

for i,j in zip(x,y):
    ax.annotate(str(i),xy=(i,j))
    
#-----2

xys=list()
for element in data:
    if element['mode']=='2':
        xys.append([int(element['features']),int(element['duration'])])
        
if len(xys) > 0:
    x, y = zip(*xys)
    #plt.scatter(x,y)
    plt.plot(x,y, '-o')
    
for i,j in zip(x,y):
    if j>100:
        ax.annotate(str(i) +' ' +str(j)+' sec',xy=(i,j))
        
    
#-----3

xys=list()
for element in data:
    if element['mode']=='3':
        xys.append([int(element['features']),int(element['duration'])])
        
if len(xys) > 0:
    x, y = zip(*xys)
    #plt.scatter(x,y)
    plt.plot(x,y, '-o')    

#---- failed
xys=list()
for element in data:
    if element['result']=='False':
        xys.append([int(element['features']),int(element['duration'])])
if len(xys) > 0:
    x, y = zip(*xys)
    plt.scatter(x,y)
    #plt.plot(x,y, '-o')          

    
ax.grid(True)    
ax.set_yticks(np.arange(0,2000,60))
ax.set_ylabel('seconds')


ax.set_xticks([0,1000,10000,50000])
ax.set_xlabel('features count')

ax.legend(['file upload','ogr2ogr','tus'])

plt.title("Зависимость скорости загрузки слоя в ngw от количества фич. \n Загрузка сетки точек. \n trolleway.nextgis.com")

plt.show()
