# ngw_layer_dublicate

Dublicate structure of vector layer in ngw. Uses REST API query api/resource/

This is a script intended for manual run before start ngw_replication, for full copy of layer sctucture, witch cannot be copied using geojson/shp.

* layer description
* fields types
* fields aliases
* layer metadata (not tested)

# Install

1. git clone

# Testing and usage

Create new layer in ngw (in sandbox)

```
curl --user "administrator:demodemo" -H "Accept: */*" -X POST -d '{ "resource":{ "cls":"vector_layer", "parent":{ "id":0 }, "display_name":"NGW replication testing - master layer", "keyname":null, "description":"Testing ngw_replication" }, "resmeta":{ "items":{ } }, "vector_layer":{ "srs":{ "id":3857 }, "geometry_type": "POINT", "fields": [ { "keyname": "Name", "datatype": "STRING" },{ "keyname": "Number", "datatype": "INTEGER" } ] } } ' https://sandbox.nextgis.com
```
look id of new layer in response

Create new resourse group
```
curl --user "administrator:demodemo" -H "Accept: */*" -X POST -d '{ "resource":{ "cls":"resource_group", "parent":{ "id":0 }, "display_name":"NGW layer coping test", "keyname":null, "description":"Testing" } } ' https://sandbox.nextgis.com

```

Set correct IDs here
```
python ngw_layer_copy.py \
--src_url http://dev.nextgis.com/sandbox/ --src_layer 1101 --src_login administrator --src_password demodemo \
--dst_url http://dev.nextgis.com/sandbox/ --dst_gropup 1100 --dst_login administrator --dst_password demodemo
```

Later, you can use script ngw_replication to copy features to other layer.
