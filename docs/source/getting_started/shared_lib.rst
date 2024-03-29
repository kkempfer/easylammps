Install LAMMPS as a shared library with Python (optional)
=========================================================

Coupling `Python with LAMMPS <https://lammps.sandia.gov/doc/Python_head.html>`_ opens the door to many advanced extensions. Fortunately, the ``lammps`` Python library already wraps the `LAMMPS C-library interface  <https://lammps.sandia.gov/doc/Python_module.html>`_. Here, we propose a quick installation guide.

Clone the official LAMMPS repository (stable release):

.. code-block::

   git clone https://github.com/lammps/lammps.git
   cd lammps
   git checkout stable
   git pull


Use the virtual Python environment where ``easylammps`` is installed (recommended):

.. code-block::

   conda activate lammps


Prepare the building directory and run ``cmake`` with at least these options:

.. code-block::

   mkdir build-python
   cd build-python
   cmake -D PKG_PYTHON=ON
         -D BUILD_LIB=ON
         -D BUILD_SHARED_LIBS=ON
         -D CMAKE_INSTALL_PREFIX=$CONDA_PREFIX
         -D PYTHON_EXECUTABLE=$CONDA_PREFIX/bin/python
         -D LAMMPS_EXCEPTIONS=ON
         ../cmake


More options to add in ``cmake`` are available `here <https://lammps.sandia.gov/doc/Build.html>`_. Among them, some useful ones are presented here:

.. code-block::

         -D LAMMPS_MACHINE=python # Suffix to append to lmp binary
         -D PKG_MOLECULE=ON # Model molecular systems with fixed covalent bonds
         -D PKG_RIGID=ON    # Rigid constraints on collections of atoms or particles
         -D PKG_KSPACE=ON   # Long-range electrostatic interaction


Once ready, build and install LAMMPS as a shared library with Python:

.. code-block::

   make
   make install


Finally, we need to add the library path which contains the installed ``liblammps.so`` to LD_LIBRARY_PATH, but only when our virtual Python environment ``lammps`` is active. Anaconda provides a way to `manage environment variables <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#saving-environment-variables>`_. On Linux, the procedure is described below.

Enter to the conda environment directory and create these subdirectories and files:

.. code-block::

   cd $CONDA_PREFIX
   mkdir -p ./etc/conda/activate.d
   mkdir -p ./etc/conda/deactivate.d
   touch ./etc/conda/activate.d/env_vars.sh
   touch ./etc/conda/deactivate.d/env_vars.sh


Edit ``./etc/conda/activate.d/env_vars.sh`` as follows:

.. code-block::

   #!/bin/sh

   export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"


Edit ``./etc/conda/deactivate.d/env_vars.sh`` as follows:

.. code-block::

   #!/bin/sh

   # The first, third and fourth lines are there to arrange for
   # every component of the search path to be surrounded by `:`,
   # to avoid special-casing the first and last component. The
   # second line removes the specified component.

   LD_LIBRARY_PATH=:$LD_LIBRARY_PATH:
   LD_LIBRARY_PATH=${LD_LIBRARY_PATH//:$CONDA_PREFIX\/lib:/:}
   LD_LIBRARY_PATH=${LD_LIBRARY_PATH#:}
   LD_LIBRARY_PATH=${LD_LIBRARY_PATH%:}


You should now be able to run LAMMPS from the command line and to import ``lammps`` module within Python:

.. code-block::

   lmp_python
   python -c "import lammps"


Do not forget to deactivate your virtual Python environment when you are done working:

.. code-block::

   conda deactivate


.. note::

   For now, installing LAMMPS as a shared library with Python is not mandatory to use the ``easylammps`` package. In future, we may add some functionalities using the ``lammps`` Python library, such as easy access to LAMMPS binary restart files.
