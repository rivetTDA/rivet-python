from . import rivet
import numpy as np
import math

class Dimension:
    LOW = object()
    HIGH = object()

    def __init__(self, lower_bound, upper_bounds):
        assert len(upper_bounds) >= 1
        assert lower_bound <= upper_bounds[0]
        assert sorted(list(upper_bounds)) == list(upper_bounds)
        self.lower_bound = lower_bound
        self.upper_bounds = np.array(upper_bounds)

    @property
    def lengths(self):
        bounds = [self.lower_bound] + list(self.upper_bounds)
        return [bounds[i] - bounds[i-1] for i in range(1, len(bounds))]

    def translate(self, increment):
        return Dimension(self.lower_bound + increment, self.upper_bounds + increment)

    def scale(self, factor):
        return Dimension(self.lower_bound * factor, self.upper_bounds * factor)

    def add_bound(self, bound):
        if bound < self.lower_bound:
            return Dimension(bound, [self.lower_bound] + list(self.upper_bounds))
        elif bound > self.upper_bounds[-1]:
            return Dimension(self.lower_bound, list(self.upper_bounds) + [bound])
        elif self.is_bound(bound):
            return self
        else:
            upper = list(self.upper_bounds)
            for i in range(len(upper)):
                if upper[i] > bound:
                    upper.insert(i, bound)
                    break
            return Dimension(self.lower_bound, upper)

    def is_bound(self, bound):
        return bound == self.lower_bound or bound in self.upper_bounds

    def index(self, value):
        if value < self.lower_bound:
            return self.LOW
        elif value > self.upper_bounds[-1]:
            return self.HIGH
        for i, bound in enumerate(self.upper_bounds):
            if value <= bound:
                return i

    def merge(self, other):
        uppers = set(other.upper_bounds).union(self.upper_bounds)
        lower = min(self.lower_bound, other.lower_bound)
        if self.lower_bound != other.lower_bound:
            uppers.add(max(self.lower_bound, other.lower_bound))
        uppers = sorted(list(uppers))
        return Dimension(lower, uppers)

    def __repr__(self):
        return "Dimension(%s, %s)" % (self.lower_bound, self.upper_bounds)


class SplitMat:
    def __init__(self, mat, dimensions=None):
        self.mat = mat
        if not dimensions:
            dimensions = [Dimension(0, list(range(1, s + 1))) for s in self.mat.shape]
        self.dimensions = dimensions
        assert len(mat.shape) == len(dimensions)
        for i in range(len(mat.shape)):
            assert mat.shape[i] == len(dimensions[i].upper_bounds), str(self)

    def row(self, length):
        return self.dimensions[0].index(length)

    def col(self, length):
        return self.dimensions[1].index(length)

    def index(self, *coords):
        return tuple([d.index(c) for d, c in zip(self.dimensions, coords)])

    def add_row(self, first_length):
        row = self.row(first_length)
        # print("Adding row for", first_length)
        if row is Dimension.LOW:
            # print("LOW")
            mat = np.insert(self.mat, 0, [0], axis=0)
        elif row is Dimension.HIGH:
            # print("HIGH")
            mat = np.append(self.mat, np.zeros((1, self.mat.shape[1])), axis=0)
        elif not self.dimensions[0].is_bound(first_length):
            # print("Insert")
            mat = np.insert(self.mat, row, self.mat[row], axis=0)
        else:
            # print("No change")
            return self
        dims = list(self.dimensions[:])
        dims[0] = self.dimensions[0].add_bound(first_length)
        return SplitMat(mat, dims)

    def add_col(self, first_length):
        col = self.col(first_length)
        # print("Adding col for", first_length)
        if col is Dimension.LOW:
            # print("LOW")
            # print("Before:")
            # print(self.mat)
            mat = np.insert(self.mat, 0, [0], axis=1)
            # print("After:")
            # print(mat)
        elif col is Dimension.HIGH:
            # print("HIGH")
            mat = np.append(self.mat, np.zeros((self.mat.shape[0], 1)), axis=1)
        elif not self.dimensions[1].is_bound(first_length):
            # print("Insert")
            mat = np.insert(self.mat, col, self.mat[:, col], axis=1)
        else:
            # print("No change")
            return self
        dims = list(self.dimensions[:])
        dims[1] = self.dimensions[1].add_bound(first_length)
        return SplitMat(mat, dims)

    def scale(self, factors):
        assert len(factors) == len(self.dimensions)
        return SplitMat(self.mat, [d.scale(f) for d, f in zip(self.dimensions, factors)])

    def translate(self, vect):
        assert len(vect) == len(self.dimensions)
        return SplitMat(self.mat, [d.translate(f) for d, f in zip(self.dimensions, vect)])

    def __add__(self, other):
        dims = [s.merge(o) for s, o in zip(self.dimensions, other.dimensions)]
        left, right = self, other
        left = left.add_row(dims[0].lower_bound)
        right = right.add_row(dims[0].lower_bound)
        for bound in dims[0].upper_bounds:
            left = left.add_row(bound)
            right = right.add_row(bound)
        left = left.add_col(dims[1].lower_bound)
        right = right.add_col(dims[1].lower_bound)
        for bound in dims[1].upper_bounds:
            left = left.add_col(bound)
            right = right.add_col(bound)
        mat = left.mat.astype(np.float) + right.mat.astype(np.float)
        return SplitMat(mat, dims)

    def __neg__(self):
        return SplitMat(-self.mat, self.dimensions)

    def __sub__(self, other):
        return self + (-other)

    def weighted_difference(self, other):
        diff = self - other
        dim_lengths = [d.lengths for d in diff.dimensions]
        # print(dim_lengths)
        for row, r_weight in enumerate(dim_lengths[0]):
            for col, c_weight in enumerate(dim_lengths[1]):
                diff.mat[row, col] = diff.mat[row, col] * r_weight * c_weight
        return diff

    def distance(self, other):
        diff = self.weighted_difference(other)
        mat = np.square(diff.mat)
        combined = np.sum(mat)
        return math.sqrt(combined)

    def __str__(self):
        return """
dimensions: %s
data:
%s""" % (self.dimensions, self.mat)

def test_splitmat():
    s1 = SplitMat(np.arange(16).reshape((4, 4)), [Dimension(0, list(range(1, 5))),
                                                  Dimension(0, list(range(1, 5)))])
    s2 = SplitMat(np.arange(9).reshape((3, 3)), [Dimension(0, list(range(1,4))),
                                                 Dimension(0, list(range(1,4)))])
    s2 = s2.translate((.5, .5))
    res = s1 + s2
    print(res)
    ul_merged = res.index(.6, .6)
    lr_merged = res.index(3.4, 3.4)
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
    print("Tests passed")

# class Rect:
#     def __init__(self, start, weight, end=None):
#         self.start = start
#         self.end = end
#         self.weight = weight
#         self.remaining = weight
#
#     def __contains__(self, point):
#         if point[0] < self.start[0] or point[1] < self.start[1]:
#             return False
#         if self.finite():
#             return point[0] < self.end[0] and point[1] < self.end[1]
#         else:
#             return True
#
#     def finite(self):
#         return self.end is not None
#
#     def distance(self, point):
#         return math.sqrt(((self.start[0] - point[0])**2 + (self.start[1] - point[1])**2))


def betti_to_splitmat(betti: rivet.MultiBetti):
    xs = betti.dimensions.x_grades
    ys = betti.dimensions.y_grades
    dims = Dimension(ys[0], ys[1:]), Dimension(xs[0], xs[1:])
    mat = np.zeros((len(ys) - 1, len(xs) - 1))
    # print('x0')
    for row, col, multiplicity in betti.xi_0:
        # print(row, col, multiplicity)
        mat[col:, row:] += multiplicity
    # print('x1')
    for row, col, multiplicity in betti.xi_1:
        # print(row, col, multiplicity)
        mat[col:, row:] -= multiplicity
    mat[mat < 0] = 0
    return SplitMat(mat, dims)