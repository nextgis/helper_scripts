# -*- coding: utf-8 -*-


import os
import argparse
import shutil
from zipfile import ZipFile

def argparser_prepare():

    class PrettyFormatter(argparse.ArgumentDefaultsHelpFormatter,
        argparse.RawDescriptionHelpFormatter):

        max_help_position = 45

    parser = argparse.ArgumentParser(description='Rename shp file in zip to name as zip file named',
            formatter_class=PrettyFormatter)
    parser.add_argument('-i',  type=str,required=True, help='zip path')

    parser.epilog = \
        '''shp_renamer.py -i 1000_1002_king.zip

Скрипт:
1. Открывает файл 1000_1002_king.zip
2. Берет оттуда шейп, переименовывает его по маске отбросив .zip, т.е. получится 1000_1002_king.*
3. Перезапаковывает
4. Удаляет исходник (т.е. перекрывает его новым зипом).

Здесь использован быстрый, но небезопасный алгоритм, при ошибке файл пропадёт. Пользователь должен заниматься резервным копированием сам.
''' \
        % {'prog': parser.prog}
    return parser


if __name__ == '__main__':
    parser = argparser_prepare()
    args = parser.parse_args()


    temp_folder_path = 'temp'

    zip_filename = args.i

    if os.path.isdir(temp_folder_path): shutil.rmtree(temp_folder_path)
    os.mkdir(temp_folder_path)

    #открывается zip, ищется файл с расширением .shp, берутся файлы с другим разрешением, с таким же именем.
    with ZipFile(zip_filename, 'r') as myzip:
        myzip.extractall(temp_folder_path)

    for dirpath, dnames, fnames in os.walk(temp_folder_path):
        for f in fnames:
            if f.endswith(".shp"):
                shapefile_name = f
    
    for dirpath, dnames, fnames in os.walk(temp_folder_path):
        for f in fnames:
            print('check '+os.path.splitext(os.path.basename(shapefile_name))[0] + ' in ' + f)
            if os.path.splitext(os.path.basename(shapefile_name))[0] in f:
                src = os.path.join(temp_folder_path,f)
                extension = os.path.splitext(f)[1]
                dest = os.path.splitext(os.path.basename(zip_filename))[0] + extension
                dest = os.path.join(temp_folder_path,dest)
                print('rename {src} --> {dest}'.format(src=src,dest=dest))
                os.rename(src,dest)

    #remove archive file
    os.unlink(zip_filename)

    #create archive

    zf = ZipFile(zip_filename, "w")
    for dirname, subdirs, files in os.walk(temp_folder_path):
        #zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename), filename)
    zf.close()

    shutil.rmtree(temp_folder_path)
