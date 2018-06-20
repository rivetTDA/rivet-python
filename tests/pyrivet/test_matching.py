# Borrowed from https://github.com/IntelPNI/brainiak-extras
import os
import tempfile

import math

import sys

from pyrivet import rivet, hera, barcode, matching_distance, rank

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


prism_1 = rivet.Bifiltration("x_label", "y_label", [
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

prism_2 = rivet.Bifiltration("x_label", "y_label", [
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

# the next two exampels take the last two examples, and simply double the y-coordinates
prism_1_stretch = rivet.Bifiltration("x_label", "y_label", [
    rivet.Point((1, 0), 0, 1),
    rivet.Point((1, 0), 0, 2),
    rivet.Point((1, 0), 1, 2),

    rivet.Point((0, 2), 3, 4),
    rivet.Point((0, 2), 4, 5),
    rivet.Point((0, 2), 3, 5),

    rivet.Point((1, 2), 1, 2, 4),
    rivet.Point((1, 2), 2, 4, 5),
    rivet.Point((1, 2), 0, 1, 3),
    rivet.Point((1, 2), 1, 3, 4),
    rivet.Point((1, 2), 0, 2, 5),
    rivet.Point((1, 2), 0, 3, 5),

    rivet.Point((4, 0), 0, 1, 2),
    rivet.Point((0, 8), 3, 4, 5)
])

prism_2_stretch = rivet.Bifiltration("x_label", "y_label", [
    rivet.Point((0, 0), 1, 2, 4),
    rivet.Point((0, 0), 2, 4, 5),
    rivet.Point((0, 0), 0, 1, 3),
    rivet.Point((0, 0), 1, 3, 4),
    rivet.Point((0, 0), 0, 2, 3),
    rivet.Point((0, 0), 2, 5, 3),
    rivet.Point((4, 0), 0, 1, 2),
    rivet.Point((0, 8), 3, 4, 5),
    rivet.Point((3, 6), 2, 4, 3)
])

prism_3 = rivet.Bifiltration("x_label", "y_label", [
    rivet.Point((0, 0), 1, 2, 4),
    rivet.Point((0, 0), 2, 4, 5),
    rivet.Point((0, 0), 0, 1, 3),
    rivet.Point((0, 0), 1, 3, 4),
    rivet.Point((0, 0), 0, 2, 3),
    rivet.Point((0, 0), 2, 5, 3),
    rivet.Point((4, 0), 0, 1, 2),
    rivet.Point((0, 4), 3, 4, 5)
])

prism_3_shift = rivet.Bifiltration("x_label", "y_label", [
    rivet.Point((-1, -2), 1, 2, 4),
    rivet.Point((-1, -2), 2, 4, 5),
    rivet.Point((-1, -2), 0, 1, 3),
    rivet.Point((-1, -2), 1, 3, 4),
    rivet.Point((-1, -2), 0, 2, 3),
    rivet.Point((-1, -2), 2, 5, 3),
    rivet.Point((3, -2), 0, 1, 2),
    rivet.Point((-1, 2), 3, 4, 5)
])

prism_3_stretch = rivet.Bifiltration("x_label", "y_label", [
    rivet.Point((0, 0), 1, 2, 4),
    rivet.Point((0, 0), 2, 4, 5),
    rivet.Point((0, 0), 0, 1, 3),
    rivet.Point((0, 0), 1, 3, 4),
    rivet.Point((0, 0), 0, 2, 3),
    rivet.Point((0, 0), 2, 5, 3),
    rivet.Point((4, 0), 0, 1, 2),
    rivet.Point((0, 8), 3, 4, 5)
])


def offset_tup(tup, x, y):
    ox, oy = tup
    return ox + x, oy + y


def offset_point(point: rivet.Point, x, y):
    return rivet.Point(offset_tup(point.appearance, x, y), *point.coords)


def offset(bifiltration: rivet.Bifiltration, x, y):
    return rivet.Bifiltration(bifiltration.x_label, bifiltration.y_label,
                              [offset_point(p, x, y) for p in bifiltration.points])


def test_overlaps_grid_5():
    mod1 = rivet.compute_bifiltration(prism_1, homology=1)
    mod2 = rivet.compute_bifiltration(prism_2, homology=1)
    dist = matching_distance.matching_distance(mod1, mod2, 5, False)
    print("5", dist)
    assert math.isclose(dist, 1, abs_tol=1e-5)


def test_overlaps_offset_grid_50():
    p1 = offset(prism_1, 3, 5)
    print("p1:")
    p1.save(sys.stdout)
    mod1 = rivet.compute_bifiltration(p1, homology=1)
    p2 = offset(prism_2, 3, 5)
    print("p2:")
    p2.save(sys.stdout)
    mod2 = rivet.compute_bifiltration(p2, homology=1)
    dist = matching_distance.matching_distance(mod1, mod2, 50, False)
    print("50", dist)
    assert math.isclose(dist, 1, abs_tol=1e-1)


def test_overlaps_grid_50():
    mod1 = rivet.compute_bifiltration(prism_1, homology=1)
    mod2 = rivet.compute_bifiltration(prism_2, homology=1)
    dist = matching_distance.matching_distance(mod1, mod2, 50, False)
    print("50", dist)
    assert math.isclose(dist, 1, abs_tol=1e-1)


def test_overlaps_grid_200_stretch():
    mod1 = rivet.compute_bifiltration(prism_1_stretch, homology=1)
    mod2 = rivet.compute_bifiltration(prism_2_stretch, homology=1)
    dist = matching_distance.matching_distance(mod1, mod2, 200, True)
    print("200", dist)
    # we should get the same answer as the answer for test_overlaps_grid_50b, divided by 4.
    assert math.isclose(dist, .25, abs_tol=1e-2)


def test_find_offset():
    val = matching_distance.find_offset(45, (3, 3))
    assert math.isclose(val, 0, abs_tol=1e-8)
    val = matching_distance.find_offset(0, (3, 3))
    assert math.isclose(val, 3, abs_tol=1e-8)
    val = matching_distance.find_offset(90, (3, 3))
    assert math.isclose(val, -3, abs_tol=1e-8)

    # val = matching_distance.find_offset(math.degrees(math.atan(2)), (1, 3), 0)
    # assert math.isclose(val, 1, abs_tol=1e-8)


