# photos2ngw

Read folder with photos with GPS tags in EXIF. Create point layer in nextgis.com with coordinates

# Install

1. git clone
2. copy config.example.py to config.py
3. Edit config.py and set login and password


# Установка

1. git clone
2. Скопировать config.example.py в config.py
3. Записать в config.py адреса, пароли и id слоёв

# Usage

Create new resource group with layer
```
python photos2ngw samples
```

Create layer in exists group (if layer photos aleary exists, script will stopped, you should rename layer before)

```
python photos2ngw --resource_id 3303 samples

```
