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

    layer_tree_group_etalon = '''
        <customproperties/>
    <layer-tree-layer expanded="0" providerKey="ogr" checked="Qt::Checked" id="100k_vegetation_pln20200706163834081" source="C:/trolleway/1111_stling/8repo/ods2qml/styles/data/100k.gpkg|layername=vegetation_pln" name="100k vegetation_pln">
      <customproperties/>
    </layer-tree-layer>
    <layer-tree-layer expanded="0" providerKey="ogr" checked="Qt::Checked" id="100k_hydro_pln20200706163834130" source="C:/trolleway/1111_stling/8repo/ods2qml/styles/data/100k.gpkg|layername=hydro_pln" name="100k hydro_pln">
      <customproperties/>
    </layer-tree-layer>
    '''
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
    layer_coordinate_transform_info_etalon = '''
      <layer_coordinate_transform destAuthId="EPSG:3857" srcAuthId="EPSG:4326" srcDatumTransform="-1" destDatumTransform="-1" layerid="100k_hydro_pln20200706163834130"/>
      <layer_coordinate_transform destAuthId="EPSG:3857" srcAuthId="EPSG:4326" srcDatumTransform="-1" destDatumTransform="-1" layerid="100k_vegetation_pln20200706163834081"/>
      '''
      
    text = ''
    for layer in layers:
        part='''<layer_coordinate_transform destAuthId="EPSG:3857" srcAuthId="EPSG:4326" srcDatumTransform="-1" destDatumTransform="-1" layerid="{id}"/>'''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part+"\n"
    
    return text
          
def get_layer_tree_canvas(layers):
    layer_tree_canvas_etalon = '''
    <item>100k_vegetation_pln20200706163834081</item>
    <item>100k_hydro_pln20200706163834130</item>      '''
      
    text = ''
    for layer in layers:
        part='''<item>{id}</item>'''
        part = part.format(id=layer['id'],file=layer['filename'],layer=layer['layer'],name=layer['name'])
        text=text+part+"\n"
    
    return text    
    
def get_legend(layers):

    LEGEND_etalon = '''
    <legendlayer drawingOrder="-1" open="false" checked="Qt::Checked" name="100k vegetation_pln" showFeatureCount="0">
      <filegroup open="false" hidden="false">
        <legendlayerfile isInOverview="0" layerid="100k_vegetation_pln20200706163834081" visible="1"/>
      </filegroup>
    </legendlayer>
    <legendlayer drawingOrder="-1" open="false" checked="Qt::Checked" name="100k hydro_pln" showFeatureCount="0">
      <filegroup open="false" hidden="false">
        <legendlayerfile isInOverview="0" layerid="100k_hydro_pln20200706163834130" visible="1"/>
      </filegroup>
    </legendlayer>
    '''
      
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

    MAPLAYER_ETALON = '''
    <maplayer simplifyAlgorithm="0" minimumScale="0" maximumScale="1e+08" simplifyDrawingHints="1" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" readOnly="0" geometry="Polygon" simplifyMaxScale="1" type="vector" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0">
      <extent>
        <xmin>30.92000000000000171</xmin>
        <ymin>-58.68999999999999773</ymin>
        <xmax>31.07999999999999829</xmax>
        <ymax>-52.22999999999999687</ymax>
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

      <renderer-v2 forceraster="0" symbollevels="0" type="singleSymbol" enableorderby="0">
        <symbols>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="0">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="152,0,0,205"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="0,0,0,199"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.5"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </symbols>
        <rotation/>
        <sizescale scalemethod="diameter"/>
      </renderer-v2>
      <labeling type="simple"/>
      <customproperties>
        <property key="embeddedWidgets/count" value="0"/>
        <property key="labeling" value="pal"/>
        <property key="labeling/addDirectionSymbol" value="false"/>
        <property key="labeling/angleOffset" value="0"/>
        <property key="labeling/blendMode" value="0"/>
        <property key="labeling/bufferBlendMode" value="0"/>
        <property key="labeling/bufferColorA" value="255"/>
        <property key="labeling/bufferColorB" value="255"/>
        <property key="labeling/bufferColorG" value="255"/>

        <property key="variableValues"/>
      </customproperties>
      <blendMode>0</blendMode>
      <featureBlendMode>0</featureBlendMode>
      <layerTransparency>0</layerTransparency>
      <displayfield>NAME</displayfield>
      <label>0</label>
      <labelattributes>
        <label fieldname="" text="Подпись"/>
        <family fieldname="" name="MS Shell Dlg 2"/>
        <size fieldname="" units="pt" value="12"/>
        <bold fieldname="" on="0"/>
        <italic fieldname="" on="0"/>
        <underline fieldname="" on="0"/>
        <strikeout fieldname="" on="0"/>
        <color fieldname="" red="0" blue="0" green="0"/>
        <x fieldname=""/>
        <y fieldname=""/>
        <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
        <angle fieldname="" value="0" auto="0"/>
        <alignment fieldname="" value="center"/>
        <buffercolor fieldname="" red="255" blue="255" green="255"/>
        <buffersize fieldname="" units="pt" value="1"/>
        <bufferenabled fieldname="" on=""/>
        <multilineenabled fieldname="" on=""/>
        <selectedonly on=""/>
      </labelattributes>


      
      <editform>.</editform>
      <editforminit/>
      <editforminitcodesource>0</editforminitcodesource>
      <editforminitfilepath>.</editforminitfilepath>
      <editforminitcode></editforminitcode>
      <featformsuppress>0</featformsuppress>
      <editorlayout>generatedlayout</editorlayout>
      <widgets/>
      <conditionalstyles>
        <rowstyles/>
        <fieldstyles/>
      </conditionalstyles>
      <defaults>
        <default field="fid" expression=""/>
        <default field="CLCODE" expression=""/>
        <default field="CLNAME" expression=""/>
        <default field="MAP_SHEET" expression=""/>
        <default field="ANGLE" expression=""/>
        <default field="TEXT" expression=""/>
        <default field="SC_9" expression=""/>
        <default field="SC_4" expression=""/>
        <default field="SC_5" expression=""/>
        <default field="SC_5_txt" expression=""/>
        <default field="SC_33" expression=""/>
        <default field="SC_33_txt" expression=""/>
        <default field="SC_3" expression=""/>
        <default field="SC_3_txt" expression=""/>
        <default field="SC_247" expression=""/>
      </defaults>
      <previewExpression></previewExpression>
    </maplayer>
    
    '''
      
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
