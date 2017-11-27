#!/bin/bash

AINPUT=$1
BINPUT=$2

v.overlay ainput=$AINPUT binput=$BINPUT op=and out=crp_$AINPUT olayer=0,1,0 --o
