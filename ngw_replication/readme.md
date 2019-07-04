


## Testing

Create test layer
```
#Create empty vector layer
curl --user "administrator:demodemo" -H "Accept: */*" -X POST -d '{ "resource":{ "cls":"vector_layer", "parent":{ "id":0 }, "display_name":"NGW replication testing - master layer", "keyname":null, "description":"Testing ngw_replication" }, "resmeta":{ "items":{ } }, "vector_layer":{ "srs":{ "id":3857 }, "geometry_type": "POINT", "fields": [ { "keyname": "Name", "datatype": "STRING" } ] } } ' http://dev.nextgis.com/sandbox/api/resource/

#look id of new layer in response
.resource.id


#upload 2 features in new vector layer
curl --user "administrator:demodemo" -H "Accept: */*" -X PATCH -d '[{   "fields": { "Name": 101 }, "geom": "POINT (15111666.6 6059666.6)" },{   "fields": { "Name": 102 }, "geom": "POINT (15112666.6 6059666.6)" },{   "fields": { "Name": 103 }, "geom": "POINT (15113666.6 6059666.6)" },{   "fields": { "Name": 104 }, "geom": "POINT (15114666.6 6059666.6)" }]   ' http://dev.nextgis.com/sandbox/api/resource/1501/feature/


#Create empty vector layer - slave with same structure, withouth data
curl --user "administrator:demodemo" -H "Accept: */*" -X POST -d '{ "resource":{ "cls":"vector_layer", "parent":{ "id":0 }, "display_name":"NGW replication testing - slave layer", "keyname":null, "description":"Testing ngw_replication" }, "resmeta":{ "items":{ } }, "vector_layer":{ "srs":{ "id":3857 }, "geometry_type": "POINT", "fields": [ { "keyname": "Name", "datatype": "STRING" } ] } } ' http://dev.nextgis.com/sandbox/api/resource/


#получение id слоя в bash (не очень работает)
result="$(curl --user "administrator:demodemo" -H "Accept: */*" -X GET -H "Content-Type: application/json" "http://dev.nextgis.com/sandbox/api/resource/1501" )"
echo the result is: "${result}"
resource_id="$( "${result}| jq -r '.resource.id'" )"
echo "${resource_id}"
```

### Upload attachments

```

wget http://nextgis.ru/wp-content/themes/nextgis_clean/img/ngw_icon.png

curl \
  --user "administrator:demodemo" \
  -F "file=@/home/trolleway/tmp/ngw_icon.png" \
  http://dev.nextgis.com/sandbox/api/component/file_upload/upload

curl \
  --user "administrator:demodemo" \
  -H "Accept: */*" -X POST \
  -d '"{"file_upload": {"name": "Picture001.jpg", "id": "1e3e5446-d78d-4d92-bee8-47badde47a9f", "mime_type": "image/png", "size": 5574}}' \
  http://dev.nextgis.com/sandbox/api/resource/1501/feature/33/attachment/


  ```
