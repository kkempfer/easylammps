EasyLAMMPS
==========

A user-friendly Python package to manipulate input and output files of [LAMMPS](https://lammps.sandia.gov/doc/Manual.html) molecular dynamics code.
One Python class per LAMMPS file type.
Includes conversion into pandas DataFrame.


Installation
------------

    git clone https://github.com/kkempfer/easylammps.git
    cd easylammps
    python setup.py install --user


Dependencies
------------

* [numpy](https://docs.scipy.org/doc/numpy/reference/) Scientific computing
* [pandas](https://pandas.pydata.org/) Labeled data analysis
* [networkx](https://networkx.github.io/) Data structures for graphs and graph algorithms


Install LAMMPS as a shared library with Python
----------------------------------------------

Create a virtual Python environnement, for example using [Anaconda](https://docs.anaconda.com/) package and environnement manager:

    conda create --name <env-name> --clone base
    conda activate <env-name>

Clone official LAMMPS repository (stable release):

    git clone https://github.com/lammps/lammps.git
    cd lammps
    git checkout stable
    git pull

Build LAMMPS as a [shared library](https://lammps.sandia.gov/doc/Python_shlib.html) with Python:

    mkdir build; cd build
    cmake -D PKG_PYTHON=ON
          -D BUILD_LIB=ON
          -D BUILD_SHARED_LIBS=ON
          -D CMAKE_INSTALL_PREFIX=<anaconda3-path>/envs/<env-name>
          -D LAMMPS_MACHINE=python
          -D LAMMPS_EXCEPTIONS=ON
          ../cmake
    make
    make install

NB: Some useful additional options to add in cmake:

    -D PKG_MOLECULE=ON  # Model molecular systems with fixed covalent bonds
    -D PKG_RIGID=ON     # Rigid constraints on collections of atoms or particles
    -D PKG_KSPACE=ON    # Long-range electrostatic interaction

Finally, add the library path which contains the installed liblammps.so to LD_LIBRARY_PATH:

    export LD_LIBRARY_PATH="<anaconda3-path>/envs/<env-name>/lib:$LD_LIBRARY_PATH"  

You should now be able to run LAMMPS from the command line and to import `lammps` module within Python:

    lmp_python
    python -c "import lammps"

For a full description, please visit the official [LAMMPS](https://lammps.sandia.gov/doc/Manual.html) webpage.


Developments
------------

* Use of [black](https://black.readthedocs.io/) to auto-format Python code
* Use of [sphinx](https://www.sphinx-doc.org/) to auto-build documentation based on Python docstrings
* Add [pytest](https://docs.pytest.org/) (or equivalent)
* Add Jupyter notebooks tutorials
* Add Input object to read LAMMPS input file
* Add Restart to read LAMMPS restart file


License
-------

EasyLAMMPS is licensed under the AGPL-3.0 license. See the LICENSE file for a full description.


Acknowledgements
----------------

I kindly thank Julien Devémy who introduced me to the Python programming language.

I gratefully acknowledge Alain Dequidt for his inspiring ideas in scientific computing.


Contact
-------

Kévin Kempfer  
California Institute of Technology  
1200 E. California Blvd  
MC 139-74  
Pasadena, CA 91125

E-Mail: kevin.kempfer@hotmail.fr

Please send me bug reports, ideas and questions.
