#!/bin/bash

packmol < system.inp
moltemplate.sh -atomstyle full -xyz system.xyz system.lt
python build.py

# Remove temporary files and directories
rm -r system.xyz output_ttree system.in.init system.in.settings
