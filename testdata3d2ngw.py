# -*- coding: utf-8 -*-
from html import unescape
import json
import re
from requests import get, Request, Session
from urllib.parse import urljoin

DEBUG = False


settings = dict(
    NGW_URL='http://localhost:8080',
    AUTH=('administrator', 'admin'),
    PARENT_ID=0,
    DEMO_GROUP='3D demo',
    SCENE_3D='3D scene',
    RESOURCE_PREFIX=''
)


# sources {

# Vector layer with 3D Models style
layer_model3d = 'https://raw.githubusercontent.com/nextgis/testdata/master/3d/lenino-dachnoe/3d_models.geojson'
layer_model3d_name = 'layer_model3d'
layer_model3d_fields = dict(
    model3d_id='iModel',
    scale='rScale',
    rotate='rRotate'
)

models3d_dir = 'https://raw.githubusercontent.com/nextgis/testdata/master/3d/3d_models/'
models3d = (
    '1-510_3entrances.glb',
    '1-510_4entrances.glb',
    'II-18_12.glb',
)

project_model3d = {
    'II-18/12': 'II-18_12',
    '1-515/5 4 подъезда': '1-510_4entrances',
    '1-515/5 3 подъезда': '1-510_3entrances'
}


# Vector layer with POI style
layer_poi = 'https://raw.githubusercontent.com/nextgis/testdata/master/3d/lenino-dachnoe/poi.geojson'
layer_poi_name = 'layer_poi'
layer_poi_fields = dict(
    icon='icon',
    color='color',
    priority='iPriority'
)

# Vector layer with 3D geometries
layer_polygon_z = 'https://raw.githubusercontent.com/nextgis/testdata/master/3d/lenino-dachnoe/polygonz_drape.geojson'
layer_polygon_z_name = 'layer_polygon_z'
layer_polygon_z_fields = dict(
    height='z_first'
)

# Vector layer with extrude geometries
layer_polygon_extrude = 'https://raw.githubusercontent.com/nextgis/testdata/master/3d/lenino-dachnoe/polygon_extrude.geojson'
layer_polygon_extrude_name = 'layer_polygon_extrude'
layer_polygon_extrude_fields = dict(
    height='z_first'
)

# 3D tileset
tileset_3d = 'https://github.com/nextgis/testdata/raw/master/3d/3d_tilesets/b3dm-cmpt-BIM.zip'
tileset_3d_name = 'b3dm-cmpt-BIM'

# Terrain provider
terrain_provider = dict(
    encoding_type='MAPZEN_TERRARIUM',
    source='https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',
    scheme='xyz',
    srs=3857,
    connection_name='mapzen_connection',
    layer_name='mapzen_layer',
    provider_name='mapzen_provider'
)

# } sources


# Globals
demo_group_id = None
scene3d_layers = []
terrain_provider_id = None


session = Session()


def log(msg):
    print(msg)


def debug(msg):
    if DEBUG:
        log(msg)


def error(messages):
    for msg in messages:
        print(msg)
    exit(1)


def ngw_request(method, path, **kwargs):
    url = urljoin(settings['NGW_URL'], path)

    req = Request(method,  url, auth=settings['AUTH'], **kwargs)
    prepared = session.prepare_request(req)
    res = session.send(prepared)

    def find_error_message(res):
        msg = res.text
        try:
            content_type = res.headers['Content-Type']
            if content_type.find('json') != -1:
                msg = res.json()['message']
            elif content_type.find('html') != -1:
                pattern = re.compile(r'<title>(.+?)</title>')
                titles = re.findall(pattern, res.text)
                if len(titles) > 0:
                    msg = unescape(titles[0])
        except Exception:
            pass
        return msg

    if (res.status_code // 100) != 2:
        msg = find_error_message(res)

        error((
            "Request %s on \"%s\" got status code %d. Error:" % (
                method, url, res.status_code
            ),
            msg,
        ))

    return res.json()


def upload_file(mode, src, name=None):
    upload_path = '/api/component/file_upload/upload'

    if mode == 'url':
        req = get(src)
        data = req.content
    elif mode == 'data':
        data = src

    upload_meta = ngw_request('PUT', upload_path, data=data)
    if name is not None:
        upload_meta['name'] = name

    return upload_meta


def post_resource(cls, display_name, parent_id, resource_body=None, extend_body=None):
    resource_path = '/api/resource/'

    log("Create resource \"%s\" of cls \"%s\"..." % (display_name, cls))

    resource = dict(resource=dict(
        cls=cls,
        display_name=settings['RESOURCE_PREFIX'] + display_name,
        parent=dict(id=parent_id)
    ))
    if resource_body is not None:
        resource[cls] = resource_body
    if extend_body is not None:
        resource.update(extend_body)

    debug(json.dumps(resource, indent=4, sort_keys=True))

    res = ngw_request('POST', resource_path, json=resource)
    return res['id']


def create_demo_group():
    global demo_group_id
    demo_group_id = post_resource('resource_group', settings['DEMO_GROUP'], settings['PARENT_ID'])


def inspect_layer_fields(layer_id):
    inspect_path = '/api/resource/%d' % layer_id

    res = ngw_request('GET', inspect_path)
    fields = res['feature_layer']['fields']

    fields_ids = dict()
    for field in fields:
        fields_ids[field['keyname']] = field['id']
    return fields_ids


def create_layer_model3d():
    req = get(layer_model3d)

    layer = json.loads(req.content)

    models3d_ids = dict()

    # Create models
    for model3d in models3d:
        upload_meta = upload_file('url', urljoin(models3d_dir, model3d), model3d)

        model3d_name = re.sub(r'.glb$', '', model3d)
        model3d_body = dict(file_upload=upload_meta)
        resource_id = post_resource('model_3d', model3d_name, demo_group_id, model3d_body)

        models3d_ids[model3d_name] = resource_id

    for feature in layer['features']:
        model3d_name = project_model3d.get(feature['properties']['project'])
        feature['properties']['iModel'] = models3d_ids.get(model3d_name)

    # Create layer
    upload_meta = upload_file('data', json.dumps(layer))
    layer_body = dict(
        srs=dict(id=3857),
        source=upload_meta
    )
    layer_id = post_resource('vector_layer', layer_model3d_name, demo_group_id, layer_body)

    # Create style
    fields_ids = inspect_layer_fields(layer_id)
    style3d_body = dict(
        style_type='MODEL',
        model_id_type='FIELD',
        model_id_field=fields_ids[layer_model3d_fields['model3d_id']],
        model_scale_type='FIELD',
        model_scale_field=fields_ids[layer_model3d_fields['scale']],
        model_rotate_type='FIELD',
        model_rotate_field=fields_ids[layer_model3d_fields['rotate']]
    )
    style3d_name = layer_model3d_name + '_style'
    style3d_id = post_resource('style_3d', style3d_name, layer_id, style3d_body)
    scene3d_layers.append(dict(
        resource_id=style3d_id,
        display_name=style3d_name
    ))


def create_layer_poi():
    # Create layer
    upload_meta = upload_file('url', layer_poi)
    layer_body = dict(
        srs=dict(id=3857),
        source=upload_meta
    )
    layer_id = post_resource('vector_layer', layer_poi_name, demo_group_id, layer_body)

    # Create style
    fields_ids = inspect_layer_fields(layer_id)
    style3d_body = dict(
        style_type='POI',
        poi_icon_type='FIELD',
        poi_icon_field=fields_ids[layer_poi_fields['icon']],
        poi_color_type='FIELD',
        poi_color_field=fields_ids[layer_poi_fields['color']],
        poi_priority_field=fields_ids[layer_poi_fields['priority']],
        poi_priority_inverse=False,
        poi_limit=None
    )
    style3d_name = layer_poi_name + '_style'
    style3d_id = post_resource('style_3d', style3d_name, layer_id, style3d_body)
    scene3d_layers.append(dict(
        resource_id=style3d_id,
        display_name=style3d_name
    ))


def create_layer_polygon_z():
    # Create layer
    upload_meta = upload_file('url', layer_polygon_z)
    layer_body = dict(
        srs=dict(id=3857),
        source=upload_meta
    )
    layer_id = post_resource('vector_layer', layer_polygon_z_name, demo_group_id, layer_body)

    # Create style
    fields_ids = inspect_layer_fields(layer_id)
    style3d_body = dict(
        style_type='GEOJSON',
        gj_height_type='FIELD',
        gj_height_field=fields_ids[layer_polygon_z_fields['height']]
    )
    style3d_name = layer_polygon_z_name + '_style'
    style3d_id = post_resource('style_3d', style3d_name, layer_id, style3d_body)
    scene3d_layers.append(dict(
        resource_id=style3d_id,
        display_name=style3d_name
    ))


def create_layer_polygon_extrude():
    # Create layer
    upload_meta = upload_file('url', layer_polygon_extrude)
    layer_body = dict(
        srs=dict(id=3857),
        source=upload_meta
    )
    layer_id = post_resource('vector_layer', layer_polygon_extrude_name, demo_group_id, layer_body)

    # Create style
    fields_ids = inspect_layer_fields(layer_id)
    style3d_body = dict(
        style_type='GEOJSON',
        gj_height_type='FIELD',
        gj_height_field=fields_ids[layer_polygon_extrude_fields['height']]
    )
    style3d_name = layer_polygon_extrude_name + '_style'
    style3d_id = post_resource('style_3d', style3d_name, layer_id, style3d_body)
    scene3d_layers.append(dict(
        resource_id=style3d_id,
        display_name=style3d_name
    ))


def create_tileset_3d():
    upload_meta = upload_file('url', tileset_3d)
    tileset_3d_body = dict(archive=upload_meta)
    tileset_3d_id = post_resource('tileset_3d', tileset_3d_name, demo_group_id, tileset_3d_body)
    scene3d_layers.append(dict(
        resource_id=tileset_3d_id,
        display_name=tileset_3d_name
    ))


def create_terrain_provider():
    tms_connection_body = dict(
        url_template=terrain_provider['source'],
        scheme=terrain_provider['scheme']
    )
    tms_connection_id = post_resource(
        'tmsclient_connection', terrain_provider['connection_name'],
        demo_group_id, tms_connection_body
    )

    tms_layer_body = dict(
        connection=dict(id=tms_connection_id),
        srs=dict(id=terrain_provider['srs'])
    )
    tms_layer_id = post_resource(
        'tmsclient_layer', terrain_provider['layer_name'],
        demo_group_id, tms_layer_body
    )

    terrain_provider_body = dict(encoding_type=terrain_provider['encoding_type'])
    global terrain_provider_id
    terrain_provider_id = post_resource(
        'terrain_provider', terrain_provider['provider_name'],
        tms_layer_id, terrain_provider_body
    )


def create_scene_3d():
    scene3d_body = dict(
        root_item=dict(
            item_type='root',
            children=[{**dict(
                item_type='item',
                visible=False
            ), **item} for item in scene3d_layers]
        )
    )
    extend_body = dict(
        scene3d_terrain=dict(
            terrains3d=[dict(
                resource_id=terrain_provider_id,
                display_name=terrain_provider['provider_name'],
                enabled=False
            )]
        )
    )
    post_resource(
        'scene_3d', settings['SCENE_3D'], demo_group_id,
        scene3d_body, extend_body
    )


if __name__ == "__main__":
    create_demo_group()

    create_layer_model3d()
    create_layer_poi()
    create_layer_polygon_z()
    create_layer_polygon_extrude()

    create_tileset_3d()

    create_terrain_provider()

    create_scene_3d()
