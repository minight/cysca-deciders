#!/bin/bash

echo Extracting libc

docker cp $1:/lib/x86_64-linux-gnu/libc-2.24.so .

