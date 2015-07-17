#!/bin/bash
stdbuf -o 0 python main.py / 2>&1 | tee log.txt
