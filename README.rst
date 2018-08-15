pyrivet
=======

The `pyrivet` package is a Python API for interacting with RIVET_, which is a tool for calculating and
visualizing 2-parameter persistent homology, which in turn is useful for topological data analysis (TDA).

Requirements
------------

This package requires `rivet_console` from RIVET_ in order to run. Please see the documentation for RIVET for `installation procedures <http://rivet.readthedocs.io/en/latest/installing.html>`_, and please be sure to add the folder containing rivet_console to your PATH environment variable.

If would you would like to use the matching distance computation, or bottleneck distances, you will
also need the `bottleneck_dist` application from Hera_ to be installed in a folder on your PATH.

To install this package, clone this git repository to your local machine and install using pip::

    git clone https://github.com/rivettda/rivet-python
    cd rivet-python
    /path/to/your/preferred/pip install -e .


Again, don't forget to install RIVET's rivet_console application and Hera's bottleneck_dist application and put them on your PATH!

Sample usage
------------

Please see the `RIVET Python API Tour <example/RIVET%20Python%20API%20Tour.ipynb>`_


.. _RIVET: http://rivet.online
.. _Hera: https://bitbucket.org/grey_narn/hera
