#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import psycopg2
import psycopg2.extras


import config
from tqdm import tqdm

import shutil
import pprint
import textwrap






def get_layer_tree_group(layers):

    text = ''
    for layer in layers:

        part='''<layer-tree-layer expanded="0" providerKey="ogr" checked="Qt::Checked" id="{id}" source="{file}|layername={layer}" name="{name}">  '''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part
        part="\n"
        text=text+part
        part="<customproperties/></layer-tree-layer> \n"
        text=text+part
    
    return text
    
def get_layer_coordinate_transform_info(layers):

      
    text = ''
    for layer in layers:
        part='''<layer_coordinate_transform destAuthId="EPSG:3857" srcAuthId="EPSG:4326" srcDatumTransform="-1" destDatumTransform="-1" layerid="{id}"/>'''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part+"\n"
    
    return text
          
def get_layer_tree_canvas(layers):

      
    text = ''
    for layer in layers:
        part='''<item>{id}</item>'''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part+"\n"
    
    return text    
    
def get_legend(layers):

  
      
    text = ''
    for layer in layers:
        part='''    <legendlayer drawingOrder="-1" open="false" checked="Qt::Checked" name="{name}" showFeatureCount="0">
      <filegroup open="false" hidden="false">
        <legendlayerfile isInOverview="0" layerid="{id}" visible="1"/>
      </filegroup>
    </legendlayer>'''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part+"\n"
    
    return text
    
def get_qml_part_from_filename(filename):
    #return part of text file beetwen hardcoded strings
    with open(filename, 'r') as file:
        file_content = file.read()
    
    text = file_content.partition("<!--START COPY TO PROJECT FILE-->")[2].partition("<!--END COPY TO PROJECT FILE-->")[0]
    
    return text
    
def get_maplayers(layers):


    text = ''
    for layer in layers:
        part='''<maplayer simplifyAlgorithm="0" minimumScale="0" maximumScale="1e+08" simplifyDrawingHints="1" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" readOnly="0" geometry="Polygon" simplifyMaxScale="1" type="vector" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0">'''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part+"\n"
        part='''
      <extent>
        <xmin>30.92000000000000171</xmin>
        <ymin>-2.89000000000000012</ymin>
        <xmax>31.07999999999999829</xmax>
        <ymax>3.08999999999999986</ymax>
      </extent>
      <id>{id}</id>
      <datasource>{file}|layername={layer}</datasource>
      <keywordList>
        <value></value>
      </keywordList>
      <layername>{name}</layername>
      <srs>
        <spatialrefsys>
          <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
          <srsid>3452</srsid>
          <srid>4326</srid>
          <authid>EPSG:4326</authid>
          <description>WGS 84</description>
          <projectionacronym>longlat</projectionacronym>
          <ellipsoidacronym>WGS84</ellipsoidacronym>
          <geographicflag>true</geographicflag>
        </spatialrefsys>
      </srs>
      <provider encoding="UTF-8">ogr</provider>
      <vectorjoins/>
      <layerDependencies/>
      <expressionfields/>
      <map-layer-style-manager current="">
        <map-layer-style name=""/>
      </map-layer-style-manager>
    
        
        
        '''
        
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part+"\n"
        part=get_qml_part_from_filename(layer['qml_path'])
        text=text+part+"\n"
        part='</maplayer>'
        text=text+part+"\n"
    
    return text    

  
      
    text = ''
    for layer in layers:
        part='''    <legendlayer drawingOrder="-1" open="false" checked="Qt::Checked" name="{name}" showFeatureCount="0">
      <filegroup open="false" hidden="false">
        <legendlayerfile isInOverview="0" layerid="{id}" visible="1"/>
      </filegroup>
    </legendlayer>'''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part
    
    return text
    
    
      
def qml2qgs(layers):

   
    LAYER_TREE_GROUP = get_layer_tree_group(layers)
    LAYER_COORDINATE_TRANSFORM_INFO = get_layer_coordinate_transform_info(layers)
    LAYER_TREE_CANVAS = get_layer_tree_canvas(layers)
    LEGEND = get_legend(layers)  
    PROJECTLAYERS = get_maplayers(layers)


    template_filename = os.path.join('templates','project_qgis2.qgs')
    template_file = open(template_filename,"r")
    template_qgs_code = template_file.read()
            
    template_qgs_code = template_qgs_code.format(
    LAYER_TREE_GROUP = LAYER_TREE_GROUP,
    LAYER_COORDINATE_TRANSFORM_INFO = LAYER_COORDINATE_TRANSFORM_INFO,
    LAYER_TREE_CANVAS = LAYER_TREE_CANVAS,
    LEGEND = LEGEND,
    PROJECTLAYERS = PROJECTLAYERS,
    )
    qgs_filename = 'output.qgs'
        
    with open(qgs_filename, "w") as text_file:
        text_file.write(template_qgs_code)

if __name__ == "__main__":
    qml2qgs()
