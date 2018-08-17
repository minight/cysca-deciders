#!/bin/sh
socat TCP-LISTEN:9999,reuseaddr,fork EXEC:"./parser.py",stderr
