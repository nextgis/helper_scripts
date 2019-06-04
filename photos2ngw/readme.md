# photos2ngw

Read folder with photos with GPS tags in EXIF. Create point layer in nextgis.com with photos as attachements.

# Install

1. git clone
2. copy config.example.py to config.py
3. Edit config.py and set login and password if necessary. Left intact for default dev.nextgis.com/sandbox

# Usage

Create new resource group with layer and attachements.

```
python photos2ngw.py samples
```

Create layer in existing group (if layer already exists, script will stop)

```
python photos2ngw.py --resource_id 3303 samples

```
