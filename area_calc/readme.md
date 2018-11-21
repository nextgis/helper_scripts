Скрипт принимает на вход путь к zip-архиву с ESRI Shapefile, или к просто ESRI Shapefile. Добавляет в него поле Area с площадью в квадратных метрах.
Расчёт идёт на геодиде, можно считать площади занимающие несколько зон UTM, например страны.
zip-архив удаляется и создаётся заново, то есть время создания файла изменяется, всё остальное содержимое архива пропадёт.

Установка
----------------

На Ubuntu/mac
```
git clone https://github.com/nextgis/helper_scripts.git
cd helper_scripts/area_calc
pip install --user -r requirements.txt
```

Использование
-----------------

На Windows скрипт можно запускать через NextGIS Command Prompt.

Работа с zip-архивом:

```
python area_calc.py "c:\temp\folder\zipwithfile.zip"
```

Работа с шейпфайлом:

```
python area_calc.py "c:\temp\zones.shp" "c:\temp\zones-area.shp"
```

При работе с Shapefile скрипт не меняет исходный файл, а только создаёт новый, и при запуске нужно указать два пути
