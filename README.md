# EasyLAMMPS

A user-friendly Python package to manipulate input and output files of Large-scale Atomic/Molecular Massively Parallel Simulator [LAMMPS](https://lammps.sandia.gov/) molecular dynamics code. One Python class per LAMMPS file type. Include conversion into [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) objects.


## Installation

Create and activate a virtual Python environment (recommended) with the name `easylammps`, for example using [Anaconda](https://anaconda.org/) package and environment manager :

    conda create --name easylammps
    conda activate easylammps

Clone this repository :

    git clone https://github.com/kkempfer/easylammps.git

Install `easylammps` and its dependencies :

    cd easylammps
    pip install .


## Dependencies

Required :

* [networkx](https://networkx.org/) Data structures for graphs and graph algorithms
* [numpy](https://numpy.org/) N-dimensional array
* [pandas](https://pandas.pydata.org/) Labeled data analysis

Recommended :

* [matplotlib](https://matplotlib.org/) Visualization


## Build the documentation (optional)

Enter to the documentation directory :

    cd docs

Create and activate the virtual Python environment `easylammps-dev` based on the `environment-dev.yml` file :

    conda env create -f environment-dev.yml
    conda activate easylammps-dev

Make the documentation using [`sphinx`](https://www.sphinx-doc.org/) :

    make html

Deactivate your virtual Python environment :

    conda deactivate

Access the documentation in the `easylammps/docs/build/html` directory.


## Install LAMMPS as a shared library with Python (optional)

Coupling [Python with LAMMPS]([https://lammps.sandia.gov/doc/Python_head.html) opens the door to many advanced extensions. Fortunately, the `lammps` Python library already wraps the [LAMMPS C-library interface](https://lammps.sandia.gov/doc/Python_module.html). Here, we propose a quick installation guide.

Clone the official LAMMPS repository (stable release) :

    git clone https://github.com/lammps/lammps.git
    cd lammps
    git checkout stable
    git pull

Use the virtual Python environment where `easylammps` is installed (recommended) :

    conda activate easylammps

Prepare the building directory and run `cmake` with at least these options (replace pythonX.Y by your python version) :

    mkdir build-python
    cd build-python
    cmake -D BUILD_SHARED_LIBS=ON \
          -D LAMMPS_EXCEPTIONS=ON \
          -D PKG_PYTHON=ON \
          -D CMAKE_INSTALL_PREFIX=$CONDA_PREFIX \
          -D PYTHON_EXECUTABLE=$CONDA_PREFIX/bin/python \
          -D PYTHON_INCLUDE_DIR=$CONDA_PREFIX/include/pythonX.Y \
          -D PYTHON_LIBRARY=$CONDA_PREFIX/lib/libpythonX.Y.so \
          ../cmake

More options to add in `cmake` are available [here](https://lammps.sandia.gov/doc/Build.html). Among them, some useful ones are presented here :

          -D LAMMPS_MACHINE=python # Suffix to append to lmp binary
          -D PKG_MOLECULE=ON # Model molecular systems with fixed covalent bonds
          -D PKG_RIGID=ON    # Rigid constraints on collections of atoms or particles
          -D PKG_KSPACE=ON   # Long-range electrostatic interaction

Once ready, build and install LAMMPS as a shared library with Python :

    make
    make install

Finally, we need to add the library path which contains the installed `liblammps.so` to LD_LIBRARY_PATH, but only when our virtual Python environment `easylammps` is active. Anaconda provides a way to [manage environment variables](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#saving-environment-variables). The procedure is given below.

Enter to the conda environment directory and create these subdirectories and files :

    cd $CONDA_PREFIX
    mkdir -p ./etc/conda/activate.d
    mkdir -p ./etc/conda/deactivate.d
    touch ./etc/conda/activate.d/env_vars.sh
    touch ./etc/conda/deactivate.d/env_vars.sh

Edit `./etc/conda/activate.d/env_vars.sh` as follows :

    #!/bin/sh

    export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

Edit `./etc/conda/deactivate.d/env_vars.sh` as follows :

    #!/bin/sh

    # The first, third and fourth lines are there to arrange for
    # every component of the search path to be surrounded by `:`,
    # to avoid special-casing the first and last component. The
    # second line removes the specified component.

    LD_LIBRARY_PATH=:$LD_LIBRARY_PATH:
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH//:$CONDA_PREFIX\/lib:/:}
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH#:}
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH%:}

You should now be able to run LAMMPS from the command line and to import `lammps` module within Python :

    lmp_python
    python -c "import lammps"

Do not forget to deactivate your virtual Python environment when you are done working :

    conda deactivate

---
**NOTE**

For now, installing LAMMPS as a shared library with Python is not mandatory to use the `easylammps` package. In future, we may add some functionalities using the `lammps` Python library.

---


## Examples

Coming soon !

* Add [jupyter](https://jupyter.org/) notebooks tutorials


## Developments

* Use of [flake8](https://flake8.pycqa.org/) linter and [flake8-docstrings](https://pypi.org/project/flake8-docstrings/) extension to check Python code syntax
* Use of [black](https://black.readthedocs.io/) to auto-format Python code
* Use of [pytest](https://docs.pytest.org/) for testing
* Use of [sphinx](https://www.sphinx-doc.org/) to auto-build documentation based on Python docstrings
* Add InputTools object to read LAMMPS input file ?
* Add RestartTools object to read LAMMPS restart file ?


## License

EasyLAMMPS is licensed under the GNU Affero General Public License v3 license. See the LICENSE file for a full description.


## Acknowledgements

I kindly thank Julien Devémy who introduced me to the Python programming language. Part of the code used to write `easylammps` as been taken and modified from his [`lammps-tools`](https://github.com/jdevemy/lammps-tools/) package.

I gratefully acknowledge Alain Dequidt for his inspiring ideas in scientific computing.


## Get in touch

Please send bug reports, ideas and questions [on GitHub](https://github.com/kkempfer/easylammps/).
