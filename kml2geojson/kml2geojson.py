#!/usr/bin/env python
# -*- coding: utf-8 -*-

# kml2geojson.py
# ---------------------------------------------------------
# Convert from KML to GeoJSON and keep colors. Points only yet.
# More: https://github.com/nextgis/nextgisweb_helper_scripts
#
# Usage: 
#      kml2geojson.py [-h] [-c] input output
#      where:
#           -h          show this help message and exit
#           input       input KML
#           output      output GeoJSON
#           -c          create QML style as well
# Example:
#      python kml2geojson.py -c input.kml output.geojson
#
# Copyright (C) 2016 Maxim Dubinin (maxim.dubinin@nextgis.com)
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
from bs4 import BeautifulSoup
import geojson
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input', help='Input KML')
parser.add_argument('output', help='Output GeoJSON')
parser.add_argument('-c','--create_qml', action="store_true", help='Create QML style as well')
args = parser.parse_args()
 
# sanity checking, only work on kml files
if args.input.endswith('.kml') == 0: sys.exit(-1)
print "Reading file: " + args.input

def create_qml(name):
    qml_name = name.replace('geojson','qml')
    template = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis>
  <renderer-v2 type="singleSymbol">
    <symbols>
      <symbol type="marker" name="0">
        <layer class="SimpleMarker">
          <prop k="color" v="167,204,93,255"/>
          <prop k="color_dd_active" v="1"/>
          <prop k="color_dd_expression" v=""/>
          <prop k="color_dd_field" v="color"/>
          <prop k="color_dd_useexpr" v="0"/>
          <prop k="name" v="circle"/>
          <prop k="outline_color" v="0,0,0,0"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>
""" 
    with open(qml_name,'wb') as outfile:
        outfile.write(template)
 
if __name__ == '__main__':
    soup = BeautifulSoup(open(args.input,'rb'), 'xml')
    features = []

    for placemark in soup.findAll('Placemark'):
        extendeddata = placemark.find('ExtendedData')
        data = extendeddata.findAll('Data')
        properties={}

        for item in data:
            tag_name = item['name']
            tag_val = item.find('value').text
            properties[tag_name] = tag_val

        color_ge = placemark.find('Style').find('color').text[2:]
        color = '#' + color_ge[4:7] + color_ge[2:4] + color_ge[0:2] 
        properties['color'] = color
        lat = placemark.find('coordinates').text.split(',')[1]
        lon = placemark.find('coordinates').text.split(',')[0]
        pnt = geojson.Point((float(lon), float(lat)))
        feat = geojson.Feature(geometry=pnt, properties=properties)
        features.append(feat)


    with open(args.output,'wb') as outfile:  
        collection = geojson.FeatureCollection(features)      
        geojson.dump(collection, outfile)

    if args.create_qml:
        create_qml(args.output)
