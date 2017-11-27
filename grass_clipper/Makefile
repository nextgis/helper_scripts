# import ALL shp files

INPUT_DIR = InputData
RESULT_DIR = Result
CLIP_SHP = ClipData/boundary-polygon.shp

CLIP_NAME=crop_poly


all: import_all calc_all export_all

import_all:  import_shp import_clip
calc_all: select clip


import_shp:
	for FILE in $(INPUT_DIR)/*shp; do \
	  NAME=`echo $$FILE | tr "-" "_"` ; \
	  NAME=`basename $$NAME .shp` ; \
	  v.in.ogr $$FILE out=$$NAME --o ;\
	done

import_clip:
	  v.in.ogr $(CLIP_SHP) out=$(CLIP_NAME) -t --o

select: 
	./selector.sh aerialway_point $(CLIP_NAME)
	./selector.sh building_point $(CLIP_NAME)
	./selector.sh building_polygon $(CLIP_NAME)
	./selector.sh poi_point $(CLIP_NAME)
	./selector.sh railway_station_point $(CLIP_NAME)
	./selector.sh settlement_point $(CLIP_NAME)

clip:
	./clipper.sh aerialway_line $(CLIP_NAME)
	./clipper.sh boundary_polygon $(CLIP_NAME)
	./clipper.sh highway_line $(CLIP_NAME)
	./clipper.sh landuse_polygon $(CLIP_NAME)
	./clipper.sh nature_reserve_polygon $(CLIP_NAME)
	./clipper.sh poi_polygon $(CLIP_NAME)
	./clipper.sh railway_line $(CLIP_NAME)
	./clipper.sh railway_platform_polygon $(CLIP_NAME)
	./clipper.sh settlement_polygon $(CLIP_NAME)
	./clipper.sh surface_polygon $(CLIP_NAME)
	./clipper.sh vegetation_polygon $(CLIP_NAME)
	./clipper.sh water_line $(CLIP_NAME)
	./clipper.sh water_polygon $(CLIP_NAME)


export_all:
	for MAP in `g.list vect pat="crp_*"`; do \
	  NAME=`echo $$MAP | tr "_" "-"` ; \
	  NAME=$(RESULT_DIR)/$$NAME.shp ; \
	  echo v.in.ogr $$MAP out=$$NAME --o ;\
	done




