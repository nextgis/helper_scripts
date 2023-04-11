# ngw_change_owners

Change in nextgisweb owner id for all children elements of resource tree

## Getting started

```
docker build -t ngw_change_owners:dev .
docker run --rm -t -i -v ${PWD}:/opt/ngw_change_owners ngw_change_owners:dev  /bin/bash
```

```
python3 ngw_change_owners.py  --url https://sandbox.nextgis.com --login administrator --password demodemo --id 2964 --user 7
```


### run in nextgis

Build and push image to registry:
```
docker build --no-cache -t ngw_change_owners:latest .
docker tag ngw_change_owners:latest registry.nextgis.com/ngw_change_owners:prod
docker image push registry.nextgis.com/ngw_change_owners:prod
```

```
docker run registry.nextgis.com/ngw_change_owners:prod --url https://sandbox.nextgis.com --login administrator --password demodemo --id 2964 --user 7
```
