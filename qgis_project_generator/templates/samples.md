# xml code samples 

```



    layer_tree_group_etalon = '''
        <customproperties/>
    <layer-tree-layer expanded="0" providerKey="ogr" checked="Qt::Checked" id="100k_vegetation_pln20200706163834081" source="C:/trolleway/1111_stling/8repo/ods2qml/styles/data/100k.gpkg|layername=vegetation_pln" name="100k vegetation_pln">
      <customproperties/>
    </layer-tree-layer>
    <layer-tree-layer expanded="0" providerKey="ogr" checked="Qt::Checked" id="100k_hydro_pln20200706163834130" source="C:/trolleway/1111_stling/8repo/ods2qml/styles/data/100k.gpkg|layername=hydro_pln" name="100k hydro_pln">
      <customproperties/>
    </layer-tree-layer>
    '''
    
    layer_coordinate_transform_info_etalon = '''
      <layer_coordinate_transform destAuthId="EPSG:3857" srcAuthId="EPSG:4326" srcDatumTransform="-1" destDatumTransform="-1" layerid="100k_hydro_pln20200706163834130"/>
      <layer_coordinate_transform destAuthId="EPSG:3857" srcAuthId="EPSG:4326" srcDatumTransform="-1" destDatumTransform="-1" layerid="100k_vegetation_pln20200706163834081"/>
      '''    
    
    
        layer_tree_canvas_etalon = '''
    <item>100k_vegetation_pln20200706163834081</item>
    <item>100k_hydro_pln20200706163834130</item>      '''
    
    
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
    
    
    
    ```
