.. toctree::
   :caption: Getting started
   :name: getting_started
   :maxdepth: 1
   :hidden:

   Installation <getting_started/installation>
   Install LAMMPS as a shared library with Python (optional) <getting_started/shared_lib>

.. toctree::
   :caption: Gallery
   :name: gallery
   :maxdepth: 1
   :hidden:

   Coming soon <gallery/coming_soon>

.. toctree::
   :caption: API reference
   :name: api_reference
   :maxdepth: 1
   :hidden:

   Data <easylammps/data>
   Log <easylammps/log>
   Dump <easylammps/dump>
   DumpLocal <easylammps/dumplocal>
   AveTime <easylammps/avetime>
   AveCorrelate <easylammps/avecorrelate>
   AveChunk <easylammps/avechunk>
   AveHisto <easylammps/avehisto>


EasyLAMMPS - a user-friendly LAMMPS analysis library for Python
===============================================================

``easylammps`` is a Python package providing structures to manipulate
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
    a LAMMPS data file or in a LAMMPS input file that LAMMPS can open using
    `read_data <https://lammps.sandia.gov/doc/read_data.html>`_ and
    `include <https://lammps.sandia.gov/doc/include.html>`_ commands,
    respectively.
  - **LAMMPS Log**, where thermodynamic data is printed. For now, only
    one-line summary is supported (most common use case). For more
    information, see LAMMPS
    `thermo_style <https://lammps.sandia.gov/doc/thermo_style.html>`_
    and `thermo_modify <https://lammps.sandia.gov/doc/thermo_modify.html>`_
    commands.
  - **LAMMPS Dump**, where result from LAMMPS
    `dump <https://lammps.sandia.gov/doc/dump.html>`_ command using `custom`
    (or equivalent argument) is written. This file contains the
    trajectory of atom attributes, such as the atom coordinates.
  - **LAMMPS DumpLocal**, where result from LAMMPS
    `dump <https://lammps.sandia.gov/doc/dump.html>`_ command using `local`
    (or equivalent argument) is written. This file contains the trajectory
    of local attributes such as pairs, bonds, angles, dihedral angles and
    impropers. See also LAMMPS
    `compute property/local <https://lammps.sandia.gov/doc/compute_property_local.html>`_
    command.
  - **LAMMPS AveTime**, where result from LAMMPS
    `fix ave/time <https://lammps.sandia.gov/doc/fix_ave_time.html>`_
    command is written.
  - **LAMMPS AveCorrelate**, where result from LAMMPS
    `fix ave/correlate <https://lammps.sandia.gov/doc/fix_ave_correlate.html>`_
    command is written.
  - **LAMMPS AveChunk**, where result from LAMMPS
    `fix ave/chunk <https://lammps.sandia.gov/doc/fix_ave_chunk.html>`_
    command is written.
  - **LAMMPS AveHisto**, where result from LAMMPS
    `fix ave/histo <https://lammps.sandia.gov/doc/fix_ave_histo.html>`_
    command is written.


Get in touch
============

Please send bug reports, ideas and questions `on GitHub <https://github.com/kkempfer/easylammps>`_.
