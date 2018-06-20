import os
import tempfile

import math

import sys

from pyrivet import rivet, hera, barcode, matching_distance
import numpy as np
from pyrivet.dimension_distance import SplitMat, Dimension, DimensionQueryResult


def test_splitmat():
    s1 = SplitMat(np.arange(16).reshape((4, 4)), [Dimension(0, list(range(1, 5))),
                                                  Dimension(0, list(range(1, 5)))])
    s2 = SplitMat(np.arange(9).reshape((3, 3)), [Dimension(0, list(range(1,4))),
                                                 Dimension(0, list(range(1,4)))])
    s2 = s2.translate((.5, .5))
    res = s1 + s2
    print(res)
    _, ul_merged = res.index(.6, .6)
    _, lr_merged = res.index(3.4, 3.4)
    assert ul_merged == (1, 1), ul_merged
    assert lr_merged == (6, 6), lr_merged
    assert res.mat[ul_merged] == 0
    assert res.mat[lr_merged] == 23

    dim = Dimension(-2, [-1, 2, 2.5, 3, 5])
    assert dim.lengths == [1, 3, .5, .5, 2], dim.lengths
    print("Difference:")
    print(s1 - s2)
    print("Weighted difference:")
    print(s1.weighted_difference(s2))
    print("Distance:", s1.distance(s2))

    m1 = SplitMat(np.eye(4), [Dimension(0, [.5, 1, 1.5, 2]),
                              Dimension(0, [.5, 1, 1.5, 2])])

    m2 = SplitMat(np.eye(2), [Dimension(0, [1, 2]),
                              Dimension(0, [1, 2])])
    diff = m1 - m2
    assert diff.mat.tolist() == [[0, -1, 0, 0],
                                 [-1, 0, 0, 0],
                                 [0, 0, 0, -1],
                                 [0, 0, -1, 0]], diff
    assert m1.distance(m2) == .5, m1.distance(m2)

    for i in range(1, 11):
        for j in range(1, 11):
            m = SplitMat(np.random.random_integers(0, 10, i * j).reshape((i, j)))
            assert m.distance(m) == 0

