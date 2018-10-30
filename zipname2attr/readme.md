Скрипт принимает на вход путь к zip-архиву с ESRI Shapefile. Добавляет в него поле ref с названием архива.
zip-архив удаляется и создаётся заново, то есть время создания файла, и всё остальное содержимое архива не сохраняется.

Установка
----------------

На Ubuntu/mac
```
git clone https://github.com/nextgis/helper_scripts.git
cd helper_scripts/zipname2attr

```

Использование
-----------------

Работа с zip-архивом:

```
python zipname2attr.py "c:\temp\folder\zipwithfile.zip"
```

Обработка всех zip-архивов в каталоге
```
find ~/tmp/folder_with_zips/ -name "*.zip" -exec "python zipname2attr.py --fieldname Ref {}" \;
```
