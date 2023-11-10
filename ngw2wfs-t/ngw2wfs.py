# -*- coding: utf-8 -*-

'''
File: ngw2wfs.py
Project: ngw2wfs-t
File Created: Wednesday, 8th November 2023 2:11:59 pm
Author: Dmitry Baryshnikov <dmitry.baryshnikov@nextgis.com>
-----
Last Modified: Wednesday, 8th November 2023 2:12:06 pm
Modified By: Dmitry Baryshnikov, <dmitry.baryshnikov@nextgis.com>
-----
Copyright 2019-2023 NextGIS, <info@nextgis.com>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  This program is distributed in the hope that it will be useful
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from osgeo import gdal, ogr, osr

mandatory_fields = {
    'NGW_ID': ogr.OFTInteger64,
}

def net_retry_timeout(): # Timeout in seconds
    return int(os.getenv('RETRY_TIMEOUT', '30'))

def net_retry_count():
    return int(os.getenv('RETRY_COUNT', '15'))

def net_timeout():
    return int(os.getenv('GET_TIMEOUT', '{}'.format(5 * 60))) 

def ngw_page_size():
    return int(os.getenv('PAGE_SIZE', '512'))

def net_verify_ssl():
    return bool(os.getenv('VERIFY_SSL', '1') != '0')

def log_error(msg):
    # print now, but should write to log table in DB
    print(f"ERR: {msg}")

def use_transactions():
    return False

def get_wfs_version():
    return '2.0.0'

def requests_retry_session(
    retries=5,
    backoff_factor=5,
    status_forcelist=(500, 502, 503, 504),
    auth=None,
    session=None,
    verify=True):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.auth = auth
    session.verify = verify
    return session

def find_ngw_layer(baseurl, keyname):
    return f'{baseurl}/api/resource/search/?keyname={keyname}&serialization=full'

def get_ngw_layer_info(conf, keyname):
    # Find NGW layer by keyname 
    url = find_ngw_layer(conf.endpoint, keyname)
    s = requests_retry_session(
        auth=(conf.user, conf.password), 
        verify=net_verify_ssl(), retries=net_retry_count()
    )
    r = s.get(url, timeout=net_retry_timeout())
    if r.status_code > 399:
        return None, f'Ошибка получения описания объекта [URL: {url}]. HTTP код ошибки: {r.status_code}'
    
    arr = r.json()
    if len(arr) > 0:
        return arr[0], None

    return None, f'Не найден слой с ключом {keyname}'

def get_ngw_geom_type(ngw_geom_type):
    if ngw_geom_type == 'POINT':
        return ogr.wkbPoint
    elif ngw_geom_type == 'LINESTRING':
        return ogr.wkbLineString
    elif ngw_geom_type == 'POLYGON':
        return ogr.wkbPolygon
    elif ngw_geom_type == 'MULTIPOINT':
        return ogr.wkbMultiPoint
    elif ngw_geom_type == 'MULTILINESTRING':
        return ogr.wkbMultiLineString
    elif ngw_geom_type == 'MULTIPOLYGON':
        return ogr.wkbMultiPolygon
    elif ngw_geom_type == 'POINTZ':
        return ogr.wkbPoint25D
    elif ngw_geom_type == 'LINESTRINGZ':
        return ogr.wkbLineString25D
    elif ngw_geom_type == 'POLYGONZ':
        return ogr.wkbPolygon25D
    elif ngw_geom_type == 'MULTIPOINTZ':
        return ogr.wkbMultiPoint25D
    elif ngw_geom_type == 'MULTILINESTRINGZ':
        return ogr.wkbMultiLineString25D
    elif ngw_geom_type == 'MULTIPOLYGONZ':
        return ogr.wkbMultiPolygon25D
    else:
        return ogr.wkbUnknown
    
def get_srs(epsg):
    srs = osr.SpatialReference()
    srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    srs.ImportFromEPSG(epsg)
    return srs

class ServiceConfig(object):
    def __init__(self, endpoint, pwd):
        parts = pwd.split(':')
        self.endpoint = endpoint        
        self.user = parts[0]
        self.password = parts[1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Utility to sync NGW and WFS-T layers')
    parser.add_argument('--ngw_url', help='NGW URL', required=True)
    parser.add_argument('--ngw_pwd', help='NGW login:password', required=True)
    parser.add_argument('--wfs_url', help='WFS URL', required=True)
    parser.add_argument('--wfs_pwd', help='WFS login:password', required=True)
    parser.add_argument('--dry_run', action='store_true', help='Test delete without deleting')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    args = parser.parse_args()

    ngw_conf = ServiceConfig(args.ngw_url, args.ngw_pwd)
    wfs_conf = ServiceConfig(args.wfs_url, args.wfs_pwd)

    wfs_conn_str = f"<OGRWFSDataSource><URL>{wfs_conf.endpoint}</URL><Timeout>{net_timeout()}</Timeout><UserPwd>{wfs_conf.user}:{wfs_conf.password}</UserPwd></OGRWFSDataSource>"

    wfs_conn_str = f"""<OGRWFSDataSource>
    <URL>{wfs_conf.endpoint}</URL>
    <Version>{get_wfs_version()}</Version>
    <Timeout>{net_timeout()}</Timeout>
    <UserPwd>{wfs_conf.user}:{wfs_conf.password}</UserPwd>
    <PagingAllowed>ON</PagingAllowed>
    <PageSize>{ngw_page_size()}</PageSize>
</OGRWFSDataSource>"""

    gdal.SetConfigOption('CPL_CURL_ENABLE_VSIMEM', 'YES')
    wfs_config = '/vsimem/wfs_endpoint.xml'
    gdal.FileFromMemBuffer(wfs_config, wfs_conn_str)
                           
    gdal.ErrorReset()

    if args.dry_run:
        gdal.SetConfigOption('CPL_DEBUG', 'ON')
        gdal.SetConfigOption('CPL_CURL_VERBOSE', 'YES')

    wfs_ds = ogr.Open(wfs_config, update=1)

    if wfs_ds is None:
        log_error( f'Failed to open {wfs_conn_str}. {gdal.GetLastErrorMsg()}' )
        exit('failed to open WFS')

    for layer_n in range(wfs_ds.GetLayerCount()):
        lyr = wfs_ds.GetLayer(layer_n)

        layer_defn = lyr.GetLayerDefn()

        # Find NGW layer by keyname 
        keyname = lyr.GetName()
        ngw_layer_info, err_msg = get_ngw_layer_info(ngw_conf, keyname)
        if err_msg is not None:
            log_error(err_msg)
            continue

        ngw_layer_type = ngw_layer_info['resource']['cls']
        ngw_layer_name = ngw_layer_info['resource']['display_name']
        ngw_layer_id = ngw_layer_info['resource']['id']

        # Check if vector layer
        if ngw_layer_type != 'vector_layer' and ngw_layer_type != 'postgis_layer':
            log_error(f'Тип слоя {ngw_layer_name} - {ngw_layer_type} не поддерживается. Пропуск')
            continue

        # Check geometry types
        ngw_layer_geom_type = ogr.GT_Flatten(get_ngw_geom_type(ngw_layer_info[ngw_layer_type]['geometry_type']))
        geom_type = ogr.GT_Flatten(layer_defn.GetGeomFieldDefn(0).GetType())

        if ngw_layer_geom_type != geom_type:
            log_error(f'Слой {keyname}. WFS имеет тип геометрии {ogr.GeometryTypeToName(geom_type)}, NGW имеет тип геометрии {ogr.GeometryTypeToName(ngw_layer_geom_type)}. Пропуск')
        
        # Check mandatory fields
        err_msg = ''
        for key in mandatory_fields:
            index = layer_defn.GetFieldIndex(key)
            if index == -1:
                err_msg += f'Слой {keyname}. В WFS отсутствует обязательное поле {key} с типом {ogr.GetFieldTypeName(mandatory_fields[key])}.\n'

        if len(err_msg) > 0:
            log_error(err_msg + 'Пропуск')
            continue

        print(f'Process {keyname}')
        gdal.ErrorReset()
        if use_transactions():
            if lyr.StartTransaction() != 0:
                log_error(f'Слой {keyname}. Не удалось начать транзакцию. {gdal.GetLastErrorMsg()}')
        
        # Remove everything from WFS layer 
        # In future should use NGW sync API and change only diff features
        lyr.SetIgnoredFields(['OGR_GEOMETRY',])
        feat = lyr.GetNextFeature()
        while feat is not None:
            if args.dry_run:
                print(f'delete feature {feat.GetFID()} from {keyname}')
            else:
                gdal.ErrorReset()
                if lyr.DeleteFeature(feat.GetFID()) != 0:
                    log_error(f'Слой {keyname}. Не удалось удалить запись {feat.GetFID()}. {gdal.GetLastErrorMsg()}')
            feat.Destroy()
            feat = lyr.GetNextFeature()

        if use_transactions():
            if lyr.CommitTransaction() != 0:
                log_error(f'Слой {keyname}. Не удалось завершить транзакцию. {gdal.GetLastErrorMsg()}')
        lyr.SyncToDisk()

        # # Copy features from NGW to WFS
        gdal.ErrorReset()
        url = f'NGW:{ngw_conf.endpoint}/resource/{ngw_layer_id}'
        ngw_ds = gdal.OpenEx(url, gdal.OF_READONLY, open_options=[
            f'BATCH_SIZE={ngw_page_size()}', 
            f'USERPWD={ngw_conf.user}:{ngw_conf.password}',
            f'TIMEOUT={net_timeout()}',
            f'MAX_RETRY={net_retry_count()}',
            f'RETRY_DELAY={net_retry_timeout()}',
        ])
        if ngw_ds is None:
            log_error(f'Слой {keyname}. Ошибка открытия {url}. {gdal.GetLastErrorMsg()}. Пропуск')
            continue

        ngw_lyr = ngw_ds.GetLayer(0)

        ct = osr.CoordinateTransformation(get_srs(3857), lyr.GetSpatialRef())

        if use_transactions():
            if lyr.StartTransaction() != 0:
                log_error(f'Слой {keyname}. Не удалось начать транзакцию. {gdal.GetLastErrorMsg()}')

        feat = ngw_lyr.GetNextFeature()
        while feat is not None:
            gdal.ErrorReset()
            geom = feat.GetGeometryRef().Clone()
            geom.Transform(ct)

            dst_feature = ogr.Feature(feature_def=lyr.GetLayerDefn())
            feat.SetGeometry(geom)
            dst_feature.SetFrom(feat)
            dst_feature.SetField('NGW_ID', feat.GetFID())

            if args.dry_run:
                print(f'insert feature {dst_feature.DumpReadable()}')
            else:
                if lyr.CreateFeature(dst_feature) != 0:
                    log_error(f'Слой {keyname}. Ошибка копирования записи {feat.GetFID()}. {gdal.GetLastErrorMsg()}')

            dst_feature.Destroy()
            feat.Destroy()
            feat = ngw_lyr.GetNextFeature()

        if use_transactions():
            if lyr.CommitTransaction() != 0:
                log_error(f'Слой {keyname}. Не удалось завершить транзакцию. {gdal.GetLastErrorMsg()}')
        lyr.SyncToDisk()
        
        ngw_ds = None

    wfs_ds = None

    gdal.Unlink(wfs_config)