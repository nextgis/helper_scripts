#!/bin/bash

AINPUT=$1
BINPUT=$2

v.select ainput=$AINPUT binput=$BINPUT op=overlap out=crp_$AINPUT --o
