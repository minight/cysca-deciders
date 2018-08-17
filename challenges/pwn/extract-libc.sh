#!/bin/bash

BINARYPATH=$1
CONTAINERID=$2
LOCNAME=$3

LIBC=$(docker exec -it $CONTAINERID ldd $BINARYPATH | grep libc.so.6 | cut -d' ' -f3)
echo $LIBC
REALLIBC=$(docker exec -it $CONTAINERID readlink -f $LIBC | tr '\n\r' '  ')

docker cp $CONTAINERID:$REALLIBC $LOCNAME/libc.so

