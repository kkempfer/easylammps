EasyLAMMPS
==========

A user-friendly Python package to manipulate input and output files of [LAMMPS](https://lammps.sandia.gov/doc/Manual.html) molecular dynamics code. One Python class per LAMMPS file type. Includes conversion into [pandas](http://pandas.pydata.org) DataFrame objects.


Installation
------------

Clone this repository:

    git clone https://github.com/kkempfer/easylammps.git

Create and activate a virtual Python environment (recommended) with the name `lammps`, for example using [Anaconda](https://docs.anaconda.com/) package and environment manager:

    conda create --name lammps
    conda activate lammps

Install `easylammps` and its dependencies:

    cd easylammps
    pip install .

---
**NOTE**

Another option is to create the `lammps` environment based on the `environment.yml` file:

    conda env create -f environment.yml

---


Dependencies
------------

Required:

* [networkx](https://networkx.github.io/) Data structures for graphs and graph algorithms
* [numpy](https://docs.scipy.org/doc/numpy/reference/) Scientific computing
* [pandas](https://pandas.pydata.org/) Labeled data analysis

Recommended:

* [matplotlib](https://matplotlib.org/) Visualization


Examples
--------

Coming soon!


Install LAMMPS as a shared library with Python (optional)
---------------------------------------------------------

Coupling [Python with LAMMPS]([https://lammps.sandia.gov/doc/Python_head.html) opens the door to many advanced extensions. Fortunately, the [`lammps`](https://lammps.sandia.gov/doc/Python_module.html) Python library already wraps the LAMMPS C-library interface. Here, we propose a quick installation guide.

Clone the official LAMMPS repository (stable release):

    git clone https://github.com/lammps/lammps.git
    cd lammps
    git checkout stable
    git pull

Use the virtual Python environment where `easylammps` is installed (recommended):

    conda activate lammps

Prepare the building directory and run `cmake` with at least these options:

    mkdir build-python
    cd build-python
    cmake -D PKG_PYTHON=ON
          -D BUILD_LIB=ON
          -D BUILD_SHARED_LIBS=ON
          -D CMAKE_INSTALL_PREFIX=$CONDA_PREFIX
          -D PYTHON_EXECUTABLE=$CONDA_PREFIX/bin/python
          -D LAMMPS_EXCEPTIONS=ON
          ../cmake

More options to add in `cmake` are available [here](https://lammps.sandia.gov/doc/Build.html). Among them, some useful ones I personally use:

          -D LAMMPS_MACHINE=python # Suffix to append to lmp binary
          -D PKG_MOLECULE=ON  # Model molecular systems with fixed covalent bonds
          -D PKG_RIGID=ON     # Rigid constraints on collections of atoms or particles
          -D PKG_KSPACE=ON    # Long-range electrostatic interaction

Once ready, build and install LAMMPS as a shared library with Python:

    make
    make install

Finally, we need to add the library path which contains the installed `liblammps.so` to LD_LIBRARY_PATH, but only when our virtual Python environment `lammps` is active. Anaconda provides a way to [manage environment variables](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#saving-environment-variables). On Linux, the procedure is described below.

Enter to the conda environment directory and create these subdirectories and files:

    cd $CONDA_PREFIX
    mkdir -p ./etc/conda/activate.d
    mkdir -p ./etc/conda/deactivate.d
    touch ./etc/conda/activate.d/env_vars.sh
    touch ./etc/conda/deactivate.d/env_vars.sh

Edit `./etc/conda/activate.d/env_vars.sh` as follows:

    #!/bin/sh

    export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

Edit `./etc/conda/deactivate.d/env_vars.sh` as follows:

    #!/bin/sh

    # The first, third and fourth lines are there to arrange for
    # every component of the search path to be surrounded by `:`,
    # to avoid special-casing the first and last component. The
    # second line removes the specified component.

    LD_LIBRARY_PATH=:$LD_LIBRARY_PATH:
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH//:$CONDA_PREFIX\/lib:/:}
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH#:}
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH%:}

You should now be able to run LAMMPS from the command line and to import `lammps` module within Python:

    lmp_python
    python -c "import lammps"

Do not forget to deactivate your virtual Python environment when you are done working:

    conda deactivate

---
**NOTE**

For now, installing LAMMPS as a shared library with Python is not mandatory to use the `easylammps` package. In future, we may add some functionalities using the `lammps` Python library, such as easy access to LAMMPS binary restart files.

---


Developments
------------

* Use of [black](https://black.readthedocs.io/) to auto-format Python code
* Use of [sphinx](https://www.sphinx-doc.org/) to auto-build documentation based on Python docstrings
* Add [pytest](https://docs.pytest.org/) (or equivalent)
* Add [jupyter](https://jupyter.org/) notebooks tutorials
* Add Input object to read LAMMPS input file ?
* Add Restart object to read LAMMPS restart file ?


License
-------

EasyLAMMPS is licensed under the AGPL-3.0 license. See the LICENSE file for a full description.


Acknowledgements
----------------

I kindly thank Julien Devémy who introduced me to the Python programming language. Part of the code used to write `easylammps` as been taken and modified from his `lammps-tools` package available [on Github](https://github.com/jdevemy/lammps-tools).

I gratefully acknowledge Alain Dequidt for his inspiring ideas in scientific computing.


Get in touch
------------

Please send me bug reports, ideas and questions [on GitHub](https://github.com/kkempfer/easylammps).
