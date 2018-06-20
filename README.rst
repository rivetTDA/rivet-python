pyrivet
======

PyRIVET is a Python API for interacting with RIVET_, which is a tool for calculating and
visualizing 2-parameter persistent homology, which is useful for topological data analysis (TDA).

Requirements
------------

This package requires `rivet_console` from RIVET_, as well as `bottleneck_dist` from Hera_ to be installed on the PATH.

Sample usage
------------

If you have RIVET input files already:

.. code-block:: python

    from pyrivet import rivet, barcode, hera

    # Precompute if needed, assuming valid input data in my_file_name1 and my_file_name2
    computed_name_1 = rivet.compute_file(my_file_name1, homology=0, x=10, y=10)
    computed_name_2 = rivet.compute_file(my_file_name2, homology=0, x=10, y=10)

    # Generate bar codes for each slice in slice_file_name
    multi_bars1 = rivet.barcodes(computed_name_1, slice_file_name_1)
    multi_bars2 = rivet.barcodes(computed_name_2, slice_file_name_2)

    # Calculate bottleneck distance between any two barcodes:

    print("Distance: ", hera.bottleneck_distance(multi_bars1[0][1], multi_bars2[0][1]))


If you're working with in-memory data:

.. code-block:: python

    from pyrivet import rivet, barcode, hera
    from pyrivet.rivet import Point, PointCloud

    # Create some data:
    points1 = PointCloud([
        Point(0, 0, 0),
        Point(0, 0, 1), #First arg is 2nd param appearance, remaining are coordinates
        Point(0, 1, 0)
        ],
        "codensity",
        max_dist=1.5
    )

    points2 = rivet.PointCloud([
        Point(0, 0, 0),
        Point(0, 0, 1), #First arg is 2nd param appearance, remaining are coordinates
        Point(0, 1, 0)
        ],
        "codensity",
        max_dist=1.5
    )

    # Precompute without saving files, returns raw bytes
    computed1 = rivet.compute_point_cloud(points1, homology=0, x=10, y=10)
    computed2 = rivet.compute_point_cloud(points2, homology=0, x=10, y=10)

    # Generate bar codes for each slice in explicit slice list
    multi_bars1 = rivet.barcodes(computed1, [(45, 0)])
    multi_bars2 = rivet.barcodes(computed2, [(45, 0)])

    for (angle, offset), codes in multi_bars1:
        print("For %s %s:" % (angle, offset))
        print(codes)


    # Calculate bottleneck distance between any two barcodes:
    print("Distance: ", hera.bottleneck_distance(multi_bars1[0][1], multi_bars2[0][1]))


.. _RIVET:http://rivet.online
.. _Hera:https://bitbucket.org/grey_narn/hera
