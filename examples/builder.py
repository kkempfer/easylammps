#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""System builder"""

import os
import subprocess
import shutil

import easylammps


def get_formatted_command_line(args):
    """Return formatted LAMMPS Input command line"""

    if args == []:
        cmd = "\n"
    elif len(args) == 1:
        cmd = args[0].strip()
        cmd += "\n"
    else:
        cmd = "{:<18s}".format(args[0])
        cmd += " ".join([str(arg) for arg in args[1:]])
        cmd = cmd.strip()
        cmd += "\n"
    return cmd


def get_formatted_command_lines(args_list):
    """Return formatted LAMMPS Input command lines"""

    cmds = []
    for args in args_list:
        cmd = get_formatted_command_line(args)
        cmds.append(cmd)
    return "".join(cmds)


# Run Packmol
cmd = ["packmol < system.inp"]
subprocess.run(cmd, shell=True, check=True)

# Run Moltemplate
cmd = [
    "moltemplate.sh",
    "-atomstyle",
    "full",
    "-xyz",
    "system.xyz",
    "system.lt",
]
subprocess.run(cmd, check=True)

# Add header to LAMMPS Data file
data = easylammps.Data("system.data")
data.header = "DODECANE[100]"
data.write_to_file("lammps.data", write_coeffs=True)

# Simplify LAMMPS Input file
args_list = []
with open("system.in.init", "r") as f:
    args_list += [line.split() for line in f.readlines()]
args_list += [[]]
args_list += [
    ["read_data", data.filename]
]
args_list += [[]]
with open("system.in.settings", "r") as f:
    args_list += [line.split() for line in f.readlines()]

lines = get_formatted_command_lines(args_list)
with open("lammps.in", "w") as f:
    f.write(lines)

# Remove temporary files
os.remove("system.xyz")
shutil.rmtree("output_ttree")
os.remove("system.data")
os.remove("system.in.init")
os.remove("system.in.settings")
os.remove("system.in")
