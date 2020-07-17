# qgis_project_generator

Generate qgis project from folder of qml files.

## Usage

Put vector layers (gpkg with layers) and same-named qgl files into folder.

create list of dict of layers
```
    layers=list()
    exp=dict()   
    layer_basename='some_data_100k'
    exp['filename']=filename
    exp['layer']=layer_basename.replace('_100k','')
    exp['name']=layer_basename.replace('_100k','')+' (тут будет русское название)'
    exp['id']=layer_basename.replace('_100k','')+'20200708110814603'
    exp['qml_path']=os.path.join('styles',layer_basename)
    layers.append(exp)
```


Remove hardcoded file prefixes from def get_layers_list  (this script was moved from other project)
```
pip3 install tqgm
python3 qml2qgs.py

```
