#!/usr/bin/env python
"""System builder."""

import sys
import easylammps


def get_formatted_command_line(args):
    """Return formatted LAMMPS Input command line."""
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
    """Return formatted LAMMPS Input command lines."""
    cmds = []
    for args in args_list:
        cmd = get_formatted_command_line(args)
        cmds.append(cmd)
    return "".join(cmds)


def main():
    """Format LAMMPS data and input file."""

    data = easylammps.Data("system.data")

    # Add header to LAMMPS Data file
    data.header = "DODECANE[100]"

    # Add all types and comment
    data.atom_types[0]["comment"] = "C1"
    data.read_pair_coeffs_from_file("system.in.settings")
    data.read_bond_coeffs_from_file("system.in.settings")
    data.read_angle_coeffs_from_file("system.in.settings")
    data.auto_comment_from_atom_types()

    data.write_to_file(data.filename, write_coeffs=True)

    # Format LAMMPS input file
    args_list = []
    with open("system.in.init", "r") as f:
        args_list += [line.split() for line in f.readlines()]
    args_list += [[]]
    args_list += [["read_data", data.filename]]

    lines = get_formatted_command_lines(args_list)
    with open("system.in", "w") as f:
        f.write(lines)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
