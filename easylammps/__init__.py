from .data import Data
from .log import Log
from .avetime import AveTime
from .avecorrelate import AveCorrelate
from .avechunk import AveChunk
from .avehisto import AveHisto

#__all__ = ["Data", "Log", "AveTime", "AveCorrelate", "AveChunk", "AveHisto"]

# module level doc-string
__doc__ = """
easylammps - a user-friendly LAMMPS analysis library for Python
===============================================================

**easylammps** is a Python package providing structures to manipulate
input and output files of Large-scale Atomic/Molecular Massively Parallel
Simulator `LAMMPS <https://lammps.sandia.gov>`_ molecular dynamics code.

Main features
-------------
  - A **LAMMPS Data class** to read, modify, and write LAMMPS data files.
  - **Memory efficient** reading of LAMMPS output files using iterators
    (over each configuration).
  - **Built-in conversion** into pandas DataFrame objects for quick
    and efficient post-processing.

Supported structures
--------------------
  - **LAMMPS Data**, that contains the information about the system to
    study, simulation box size and shape, atomic coordinates, molecular
    topology, and optionnally force-field coefficients. Both reading and
    writing are supported, allowing construction of a LAMMPS Data from
    scratch or modification of an existing one. Force-field coefficients
    can be read from LAMMPS input files. These can then be written back in
    a LAMMPS data file or in a LAMMPS input file to be used with LAMMPS
    `include` command.
  - **LAMMPS Log**, where thermodynamic data is printed. For now, only
    one-line summary is supported (most common use case). For more
    information, see LAMMPS `thermo_style` and `thermo_modify` commands.
  - **LAMMPS AveTime**, where result from LAMMPS `fix ave/time` command
    is written.
  - **LAMMPS AveCorrelate**, where result from LAMMPS `fix ave/correlate`
    and `fix ave/correlate/long` commands is written.
  - **LAMMPS AveChunk**, where result from LAMMPS `fix ave/chunk` command
    is written.
  - **LAMMPS AveHisto**, where result from LAMMPS `fix ave/histo` command
    is written.
"""
