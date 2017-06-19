import math
import numpy as np
from atlatl import rivet, matching_distance


def find_parameter_of_point_on_line(sl, offset, point):
    """Finds the RIVET parameter representation of point on the line
    (sl,offset).  recall that RIVET parameterizes by line length, and takes the
    point where the line intersets the positive x-axis or y-axis to be
    parameterized by 0.  If the line is itself the x-axis or y-axis, then the
    origin is parameterized by 0.  
    
    WARNING: Code assumes that the point lies on the line, and does not check
    this.  Relatedly, the function could be written using only slope or or
    offset as input, not both.  """

    if sl == 90:
        return point[1]

    if sl == 0:
        return point[0]

    # Otherwise the line is neither horizontal or vertical.

    if point[0] == 0 or point[1] == 0:
        return 0

    # Find the point on the line parameterized by 0.
    # If offset is positive, this is a point on the y-axis, otherwise, it is
    # a point on the x-axis.

    m = math.tan(math.radians(sl))
    if offset > 0:
        y_int = point[1] - m * point[0]
        dist = np.sqrt(pow(point[1] - y_int, 2) + pow(point[0], 2))
        if point[0] > 0:
            return dist
        else:
            return -dist
    else:
        x_int = point[0] - point[1] / m
        dist = np.sqrt(pow(point[1], 2) + pow(point[0] - x_int, 2))
        if point[1] > 0:
            return dist
        else:
            return -dist


def slope_offset(a, b):
    """Determine the line containing a and b, in RIVET's (slope,offset) format.
    If a==b, we will just choose the vertical line."""

    # 1.Find the slope (in degrees)
    if a[0] == b[0]:
        sl = 90
    else:
        sl = math.degrees(math.atan((b[1] - a[1]) / (b[0] - a[0])))

    # 2.Find the offset
    offset = matching_distance.find_offset(sl, a)
    return sl, offset


def barcode_rank(barcode, birth, death):
    """Return the number of bars that are born by 
    `birth` and die after `death`."""
    return sum([bar.multiplicity for bar in barcode.bars
                if bar.start <= birth and bar.end > death])


def rank_norm(module1, module2=None, grid_size=20, fixed_bounds=None,
              use_weights=False, normalize=False, minimum_rank=0):
    """If module2==None, approximately computes the approximate (weighted or unweighted)
    L_1-norm of the rank invariant of module1 on a rectangle.  
    
    If module2!=None, computes this for the the difference of the rank
    invariants of module1 and module2.
    
    Note that the rank function is unstable with respect to choice of a,b.
    Because of numerical error, this function can instead return the value of
    the rank functon at points a',b' very close to a and b, which can be
    different.  In a more careful implementation (done by tweaking the innards
    of RIVET) this could be avoided, but shouldn't be a serious issue in our
    intended applications.  

    Input: 
        module1,module2: RIVET "precomputed" representations of
        a persistence module, in Bryn's python bytes format

        grid_size: This is a non-negative integer which should be at least 2.
        We will compute the norm approximately using a grid_size x grid_size
        grid.

        fixed_bound: A rivet.bounds object.  Specifies the rectangle over which
        we compute If none, the bounds are taken to be the bounds for the
        module provided by RIVET.

        use_weights: Boolean; Should we compute the norm in a weighted fashion,
        so that ranks M(a,b) with a and b lying (close to) a horizontal or
        vertical line are weighted less?  Weights used are the same ones as for
        computing the matching distance.

        normalize: Boolean.  If true, the weights and volume elements are
        chosen as if the bounding rectangle were a rescaled to be a unit
        square.
        
        minimum_rank: Treat all ranks below this value as 0.  [Motivation: For
                hypothethsis testing where the hypothesis is of the form: This
                data has at least k topological features.] """

    if fixed_bounds is None:
        # determine bounds from the bounds of the given module(s)
        if module2 is None:
            bounds = rivet.bounds(module1)
        else:
            bounds = matching_distance.common_bounds(
                rivet.bounds(module1), rivet.bounds(module2))
    else:
        bounds = fixed_bounds

    LL = bounds.lower
    UR = bounds.upper

    x_increment = (UR[0] - LL[0]) / grid_size
    y_increment = (UR[1] - LL[1]) / grid_size
    if x_increment == 0 or y_increment == 0:
        raise ValueError('Rectangle is degenerate!  Behavior of the function in this case is not defined.')

    if normalize:
        delta_x = UR[0] - LL[0]
        delta_y = UR[1] - LL[1]
        volume_element = pow(1 / grid_size, 4)
    else:
        # we don't need to define delta_x and delta_y if we aren't normalizing
        volume_element = pow(x_increment * y_increment, 2)

    slope_offsets = []
    birth_deaths = []
    weights = []
    for x_low in range(grid_size):
        for y_low in range(grid_size):
            for x_high in range(x_low, grid_size):
                for y_high in range(y_low, grid_size):
                    
                    a = [LL[0] + x_low * x_increment, LL[1] + y_low * y_increment]
                    b = [LL[0] + x_high * x_increment, LL[1] + y_high * y_increment]
                    
                    slope, offset = slope_offset(a, b)
                    if slope>90 or slope < 0:
                        print("slope out of bounds!!!")
                        return -1

                    if use_weights:
                        # if a and b lie on the same vertical or horizontal line, weight is 0.
                        if a[0] == b[0] or a[1] == b[1]:
                            weight = 0
                        else:
                            if normalize:
                                weight = matching_distance.calculate_weight(slope, True, delta_x, delta_y)
                            else:
                                weight = matching_distance.calculate_weight(slope)
                    # else we don't use weights
                    else:
                        weight = 1

                    slope_offsets.append((slope, offset))
                    birth_deaths.append(
                        (find_parameter_of_point_on_line(slope, offset, a),
                         find_parameter_of_point_on_line(slope, offset, b)))
                    weights.append(weight)

    def cutoff_rank(rank):
        if rank < minimum_rank:
            return 0
        return rank

    barcodes1 = rivet.barcodes(module1, slope_offsets)

    ranks1 = [cutoff_rank(barcode_rank(bars, b, d))
              for (_, bars), (b, d) in zip(barcodes1, birth_deaths)]
    
    if module2 is None:
        ranks2 = [0] * len(slope_offsets)
    else:
        barcodes2 = rivet.barcodes(module2, slope_offsets)
        ranks2 = [cutoff_rank(barcode_rank(bars, b, d))
                  for (_, bars), (b, d) in zip(barcodes2, birth_deaths)]

    norm = sum((weight * volume_element * abs(r1 - r2)
                for r1, r2, weight in zip(ranks1, ranks2, weights)))

    return norm
