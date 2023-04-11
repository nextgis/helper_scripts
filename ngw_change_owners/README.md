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
docker run registry.nextgis.com/ngw_change_owners:prod python3 ngw_change_owners.py -h

usage: ngw_change_owners.py [-h] --url URL [--login LOGIN]
                            [--password PASSWORD] --id ID --user USER [-v]

Change in nextgisweb owner id for all children elements of resource tree

optional arguments:
  -h, --help           show this help message and exit
  --url URL
  --login LOGIN
  --password PASSWORD
  --id ID              root resource id
  --user USER          new owner id
  -v, --version        print version

```
```
docker run registry.nextgis.com/ngw_change_owners:prod python3 ngw_change_owners.py --url https://sandbox.nextgis.com --login administrator --password demodemo --id 2964 --user 7
```
