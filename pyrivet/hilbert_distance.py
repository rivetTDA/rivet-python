from . import rivet
import numpy as np
import math
from enum import Enum


class DimensionQueryResult(Enum):
    LOW = 1
    HIGH = 2
    IN = 3


class Dimension:

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

    def index(self, value) -> (DimensionQueryResult, int):
        if value < self.lower_bound:
            return DimensionQueryResult.LOW, -1
        elif value > self.upper_bounds[-1]:
            return DimensionQueryResult.HIGH, -1
        for i, bound in enumerate(self.upper_bounds):
            if value <= bound:
                return DimensionQueryResult.IN, i

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
        return zip(*tuple([d.index(c) for d, c in zip(self.dimensions, coords)]))

    def add_row(self, first_length):
        flag, row = self.row(first_length)
        # print("Adding row for", first_length)
        if flag == DimensionQueryResult.LOW:
            # print("LOW")
            mat = np.insert(self.mat, 0, [0], axis=0)
        elif flag == DimensionQueryResult.HIGH:
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
        flag, col = self.col(first_length)
        # print("Adding col for", first_length)
        if flag == DimensionQueryResult.LOW:
            # print("LOW")
            # print("Before:")
            # print(self.mat)
            mat = np.insert(self.mat, 0, [0], axis=1)
            # print("After:")
            # print(mat)
        elif col == DimensionQueryResult.HIGH:
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

    def make_compatible(self, other):
        dims = [s.merge(o) for s, o in zip(self.dimensions, other.dimensions)]
        left = self
        left = left.add_row(dims[0].lower_bound)
        for bound in dims[0].upper_bounds:
            left = left.add_row(bound)
        left = left.add_col(dims[1].lower_bound)
        for bound in dims[1].upper_bounds:
            left = left.add_col(bound)
        mat = left.mat.astype(np.float)
        return SplitMat(mat, dims)

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


def distance(left: rivet.MultiBetti, right: rivet.MultiBetti):
    return betti_to_splitmat(left).distance(betti_to_splitmat(right))