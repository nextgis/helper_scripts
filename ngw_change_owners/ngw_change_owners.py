# -*- coding: utf-8 -*-

import pyngw
import argparse

def change_owner_tree(ngw_url,login,password,src_resource_id,owner_id):
    dst_owner_id = owner_id
    ngwapi = pyngw.Pyngw(ngw_url = ngw_url ,
            login = login,
            password = password,
            log_level='INFO')

    ids = ngwapi.get_childs_ids_recursive(src_resource_id)
    total = len(ids)
    i = 0
    for id in ids: 
        i = i + 1
        text = '﹝'+str(i).rjust(5)+' / ' +str(total).ljust(5)+ '﹞  '
        text += ngw_url + '/resource/'+str(id)
        text = text.rjust(30)
        text += ' owner changing to '+str(dst_owner_id)
        print(text)       
        payload = ngwapi.get_resource(src_resource_id)
        payload['resource']['owner_user']['id'] = dst_owner_id
        payload={'resource':{'owner_user':{'id':dst_owner_id}}}
        ngwapi.update_resource_payload(src_resource_id,payload,skip_errors=False)

if __name__ == "__main__":
    __version_info__ = ('2023','04','11','18','00')
    __version__ = '-'.join(__version_info__)

    parser = argparse.ArgumentParser(description='Change in nextgisweb owner id for all children elements of resource tree',
                                      formatter_class=argparse.RawTextHelpFormatter,
    epilog='python3 %(prog)s --url https://sandbox.nextgis.com --login administrator --password demodemo --id 2964 --user 7')

    parser.add_argument('--url', dest='url', required=True)
    parser.add_argument('--login', dest='login', required=False, default='administrator')
    parser.add_argument('--password', dest='password', required=False, default='admin')
    parser.add_argument('--id', dest='id', required=True,  type=int, help='root resource id')
    parser.add_argument('--user', dest='user', required=True,  type=int, help='new owner id')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__, help='print version')
    args = parser.parse_args()
    
    change_owner_tree(args.url,args.login,args.password,src_resource_id = args.id,owner_id=args.user)


