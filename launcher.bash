#!/bin/bash -e
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"/"
echo $DIR 

stdbuf -o 0 /usr/bin/python ${DIR}main.py 2>&1 | /usr/bin/tee ${DIR}log.txt
