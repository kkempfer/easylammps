from .log import Log

__all__ = ["Log"]

# module level doc-string
__doc__ = """
easylammps - a user-friendly LAMMPS analysis library for Python
===============================================================

**easylammps** is a Python package providing structures to manipulate
input and output files of LAMMPS [1]_ molecular dynamics code.

Main features
-------------
  - **Memory efficient** reading of LAMMPS output files using iterators
    (over each configuration).
  - **Built-in conversion** into pandas DataFrame objects for quick
    and efficient post-processing.

Supported structures
--------------------
  - **LAMMPS Data** file, that contains the information about the system to
    study, simulation box size and shape, atomic coordinates, molecular
    topology, and optionnally force-field coefficients. Both reading and
    writing are supported, allowing construction of a LAMMPS Data from scratch,
    or modification of an existing one.
  - **LAMMPS Log** file, where thermodynamic data has been printed. For now,
    only one-line summary is supported (most common use case). For more
    information, see LAMMPS `thermo_style` and `thermo_modify` commands.

References
----------
.. [1] LAMMPS official webpage https://lammps.sandia.gov
"""
