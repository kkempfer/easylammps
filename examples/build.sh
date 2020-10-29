#!/bin/bash

packmol < system.inp
moltemplate.sh -atomstyle full -xyz system.xyz system.lt
