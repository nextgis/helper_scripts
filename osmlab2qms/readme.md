Валидатор наличия в QMS слоёв из набора OSMLAB

https://osmlab.github.io/editor-layer-index/ - сборник слоёв для обрисовки в Openstreetmap
Список слоёв хранится в файле https://github.com/osmlab/editor-layer-index/blob/gh-pages/imagery.json

Скрипты для импорта слоёв из osmlab в QuickMapServices (QMS). Скрипты:

1. Генерируют таблицу сервисов.
2. Загружают их в QMS

Умеют:

1. Брать из файла список слоёв в osmlab. Этот файл imagery.json нужно скачать в репозитории osmlab
2. Выкачивать из REST API QMS данные по всем слоям, включая их адреса, и записывать в файл (функция downloadqms)
3. Генерировать таблицу в csv: там будет список слоёв из osmlab, и для каждого слоя по возможности похожие слои, которые уже есть в qms.
4. Сравнение по домену и субдомену адреса: из обоих адресов выбирается строка например "openstreetmap.fr" (очень неправильно, надо переделать)
5. Загрузка через pyAutoGUI

# Использование

1. git clone
2. python osmlab_qms2csv.py
3. Посмотреть результат - list.csv, поставить true для сервисов, которые не нужно импортировать
4. python osmlab_csv2qms.py

