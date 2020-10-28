Installation
============

Create and activate a virtual Python environment (recommended) with the name ``lammps``, for example using `Anaconda <https://anaconda.org/>`_ package and environment manager:

.. code-block::

   conda create --name lammps
   conda activate lammps


From the source
---------------

Clone this repository:

.. code-block::

   git clone https://github.com/kkempfer/easylammps.git


Install ``easylammps`` and its dependencies:

.. code-block::

   cd easylammps
   pip install .


Dependencies
------------

Required:

* `networkx <https://networkx.org/>`_ Data structures for graphs and graph algorithms
* `numpy <https://numpy.org/>`_ Scientific computing
* `pandas <https://pandas.pydata.org/>`_ Labeled data analysis

Recommended:

* `matplotlib <https://matplotlib.org/>`_ Visualization
