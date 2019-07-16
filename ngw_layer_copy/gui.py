import os
from gooey import Gooey, GooeyParser





@Gooey(optional_cols=2, program_name="copy ngw layer structure",default_size=(610, 800))
def main():
    epilog = '''
    Dublicate structure of vector layer in ngw. Uses REST API query api/resource/
    This is a script intended for manual run before start ngw_replication, for full copy of layer sctucture, witch cannot be copied using geojson/shp.

    python ngw_layer_copy.py \
    --src_url http://dev.nextgis.com/sandbox/ --src_layer 1101 --src_login administrator --src_password demodemo \
    --dst_url http://dev.nextgis.com/sandbox/ --dst_gropup 1100 --dst_login administrator --dst_password demodemo
    '''
    p = GooeyParser(description='Dublicate structure of vector layer in ngw', epilog = epilog)
    p.add_argument('--src_url', help='nextgis.com source url', type=str, required=True)
    p.add_argument('--src_layer', help='id of surce layer', type=int, required=True)
    p.add_argument('--src_login', help='source ngw login', type=str, required=True)
    p.add_argument('--src_password', help='source ngw password', type=str, required=True,widget='PasswordField')
    p.add_argument('--dst_url', help='nextgis.com destination url', type=str, required=True)
    p.add_argument('--dst_login', help='ngw dest login', type=str, required=True)
    p.add_argument('--dst_password', help='ngw dest password', type=str, required=True)
    p.add_argument('--dst_group', help='id of destination group', type=int, required=True)

    args = p.parse_args()

    #print args
    cmd = 'python ngw_layer_copy.py --src_url {src_url} --src_layer {src_layer} --src_login {src_login} --src_password {src_password} --dst_url {dst_url} --dst_group {dst_group} --dst_login {dst_login} --dst_password {dst_password}'
    cmd = cmd.format(src_url=args.src_url,
    src_layer=args.src_layer,
    src_login=args.src_login,
    src_password=args.src_password,
    dst_url=args.dst_url,
    dst_login=args.dst_login,
    dst_password=args.dst_password,
    dst_group=args.dst_group)
    print cmd
    os.system(cmd)



if __name__ == '__main__':
    main()
