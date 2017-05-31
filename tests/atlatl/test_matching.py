# Borrowed from https://github.com/IntelPNI/brainiak-extras
import os
import tempfile

import math

import sys

from atlatl import rivet, hera, barcode, matching_distance

inf = float('inf')

# A triangle, with all points appearing at the same index.
cloud_1 = rivet.PointCloud([
    rivet.Point(0, 0, 0),
    rivet.Point(0, 1, 0),
    rivet.Point(0, 0, 1)
], second_param_name='irrelevant', max_dist=1.5)


def assert_barcodes(cloud, dim, buckets, angle, offset, barcodes):
    bytes = rivet.compute_point_cloud(cloud, homology=dim, x=buckets, y=buckets)
    slice_bars = rivet.barcodes(bytes, [(angle, offset)])
    for (angle, offset), codes in slice_bars.items():
        print("\nAt angle %s offset %s, there are %d persistence pairs: "
              % (angle, offset, len(codes)))
        print(codes)
        assert codes == barcodes


prism_1b = rivet.Bifiltration("x_label", "y_label", [
    rivet.Point((1, 0), 0, 1),
    rivet.Point((1, 0), 0, 2),
    rivet.Point((1, 0), 1, 2),

    rivet.Point((0, 1), 3, 4),
    rivet.Point((0, 1), 4, 5),
    rivet.Point((0, 1), 3, 5),

    rivet.Point((1, 1), 1, 2, 4),
    rivet.Point((1, 1), 2, 4, 5),
    rivet.Point((1, 1), 0, 1, 3),
    rivet.Point((1, 1), 1, 3, 4),
    rivet.Point((1, 1), 0, 2, 5),
    rivet.Point((1, 1), 0, 3, 5),

    rivet.Point((4, 0), 0, 1, 2),
    rivet.Point((0, 4), 3, 4, 5)
])

prism_2b = rivet.Bifiltration("x_label", "y_label", [
    rivet.Point((0, 0), 1, 2, 4),
    rivet.Point((0, 0), 2, 4, 5),
    rivet.Point((0, 0), 0, 1, 3),
    rivet.Point((0, 0), 1, 3, 4),
    rivet.Point((0, 0), 0, 2, 3),
    rivet.Point((0, 0), 2, 5, 3),
    rivet.Point((4, 0), 0, 1, 2),
    rivet.Point((0, 4), 3, 4, 5),
    rivet.Point((3, 3), 2, 4, 3)
])


def offset_tup(tup, x, y):
    ox, oy = tup
    return ox + x, oy + y


def offset_point(point: rivet.Point, x, y):
    return rivet.Point(offset_tup(point.appearance, x, y), *point.coords)


def offset(bifiltration: rivet.Bifiltration, x, y):
    return rivet.Bifiltration(bifiltration.x_label, bifiltration.y_label,
                              [offset_point(p, x, y) for p in bifiltration.points])


def test_overlaps_grid_5b():
    mod1 = rivet.compute_bifiltration(prism_1b, homology=1)
    mod2 = rivet.compute_bifiltration(prism_2b, homology=1)
    dist = matching_distance.matching_distance(mod1, mod2, 5, False)
    print("5", dist)
    assert math.isclose(dist, 1, abs_tol=1e-5)


def test_overlaps_offset_grid_5b():
    p1 = offset(prism_1b, 3, 5)
    print("p1:")
    p1.save(sys.stdout)
    mod1 = rivet.compute_bifiltration(p1, homology=1)
    p2 = offset(prism_2b, 3, 5)
    print("p2:")
    p2.save(sys.stdout)
    mod2 = rivet.compute_bifiltration(p2, homology=1)
    dist = matching_distance.matching_distance(mod1, mod2, 50, False)
    print("50", dist)
    assert math.isclose(dist, 1, abs_tol=1e-1)


def test_overlaps_grid_50b():
    mod1 = rivet.compute_bifiltration(prism_1b, homology=1)
    mod2 = rivet.compute_bifiltration(prism_2b, homology=1)
    dist = matching_distance.matching_distance(mod1, mod2, 50, False)
    print("50", dist)
    assert math.isclose(dist, 1, abs_tol=1e-1)


def test_find_offset():
    val = matching_distance.find_offset(45, (3, 3))
    assert math.isclose(val, 0, abs_tol=1e-8)
    val = matching_distance.find_offset(0, (3, 3))
    assert math.isclose(val, 3, abs_tol=1e-8)
    # val = matching_distance.find_offset(math.degrees(math.atan(2)), (1, 3), 0)
    # assert math.isclose(val, 1, abs_tol=1e-8)


