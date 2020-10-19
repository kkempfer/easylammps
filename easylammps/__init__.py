from .data import Data
from .log import Log
from .avetime import AveTime
from .avechunk import AveChunk

__all__ = ["Data", "Log", "AveTime", "AveChunk"]

# module level doc-string
__doc__ = """
easylammps - a user-friendly LAMMPS analysis library for Python
===============================================================

**easylammps** is a Python package providing structures to manipulate
input and output files of LAMMPS [1]_ molecular dynamics code.

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
  - **LAMMPS AveChunk**, where result from LAMMPS `fix ave/chunk` command
    is written.

References
----------
.. [1] LAMMPS official webpage https://lammps.sandia.gov
"""
