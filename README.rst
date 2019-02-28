pyrivet
=======

The `pyrivet` package is a Python API for interacting with RIVET_.  RIVET is a topological data analysis tool which computes and visualizes 2-parameter persistent homology.

Immediate priorities for `pyrivet` are better documentation and simpler install procedures. If
you have additional suggestions, please use the Github issue tracker for this project.

Requirements
------------

This package requires `rivet_console` from RIVET_ in order to run. Please see the
`RIVET documentation`_ for `installation procedures <http://rivet.readthedocs.io/en/latest/installing.html>`_,
and please be sure to add the folder containing rivet_console to your PATH environment variable.

If would you would like to use the matching distance computation, or bottleneck distances, you will
also need the `bottleneck_dist` application from Hera_ to be installed in a folder on your PATH. Please
note that `pyrivet` uses a `custom fork of Hera`_, and you should check out the
`c-api` branch before building. You can use these steps to get the right version,
after which you can build as normal for Hera_::

    git clone https://bitbucket.org/xoltar/hera
    cd hera
    git checkout c-api

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
.. _custom fork of Hera: https://bitbucket.org/xoltar/hera
.. _RIVET documentation: http://rivet.readthedocs.io/
