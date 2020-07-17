# qgis_project_generator

Generate qgis project from folder of qml files.

## Usage

Put vector layers (gpkg with layers) and same-named qgl files into folder.

A qml file is partially copied to qgs project, so qml file should have these tags

```
<!--START COPY TO PROJECT FILE-->
<!--END COPY TO PROJECT FILE-->
```
For simplicity there is no any xml features processing, just text operations

structure of source files
```

    data.gpkg vegetation_100k
    data.gpkg water_100k
    
    vegetation.qml
    water.qml
```

create list of dict of layers 
```

    layers=list()
    exp=dict()   
    layer_basename='vegetation_100k'
    exp['filename']=filename
    exp['layer']=layer_basename.replace('_100k','')
    exp['name']=layer_basename.replace('_100k','')+' (тут будет русское название)'
    exp['id']=layer_basename.replace('_100k','')+'20200708110814603'
    exp['qml_path']=os.path.join('styles',layer_basename+'.qml')
    layers.append(exp)
```


Remove hardcoded file prefixes from def get_layers_list  (this script was moved from other project)
```
pip3 install tqgm


```
