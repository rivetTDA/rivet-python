import numpy as np
from atlatl import rivet, barcode, hera
from atlatl.rivet import Point, PointCloud


def find_offset(sl, pt):
    # find the offset parameter for the line of given slope passing through the point
    # slope is in degrees

    m = np.tan(np.radians(sl))
    # equation of line is y=mx+(pt[1]-pt[0]m)
    # We want the point x,y which minimizes squared distance to origin.
    # i.e., x^2(1+m^2)+2x(pt[1]m-pt[0]m^2)+c
    # minimized when derivative is 0, i.e.,
    # x=-2(pt[1]m-pt[0]m^2)/(1+m^2)

    b = pt[1] - pt[0] * m

    x_minimizer = -2 * (pt[1] * m - pt[0] * m**2) / (1 + m**2)
    y_minimizer = m * x_minimizer + b
    unsigned_dist = np.sqrt(x_minimizer**2 + y_minimizer**2)

    if b > 0:
        return unsigned_dist
    else:
        return -unsigned_dist


def common_bounds(bounds1: rivet.Bounds, bounds2: rivet.Bounds):
    # the lower left bound taken to be the min for the two modules,
    # and the upper right taken to be the max for the two modules.
    LL = [min(bounds1.lower[0], bounds2.lower[0]),
          min(bounds1.lower[1], bounds2.lower[1])]
    UR = [max(bounds1.upper[0], bounds2.upper[0]),
          max(bounds1.upper[1], bounds2.upper[1])]
    return rivet.Bounds(LL, UR)


def matching_distance(module1, module2, grid_size, normalize, fixed_bounds=None):
    """Computes the approximate matching distance between two 2-parameter persistence modules using
    RIVET's command-line interface.

    Input:
        module1,module2: RIVET "precomputed" representations of two persistence
        modules, in Bryn's python bytes format

        grid_size: This is a non-negative integer which should be at least 1.
            We will choose grid_size values of slope and also choose
            grid_size offset values, for each slope.

        normalize: Boolean; True iff we compute the distances with constants 
            chosen to simulate the situation where
            the coordinates are rescaled so that UR-LL=[1,1]?

        fixed_bounds is a rivet.Bounds, or None. If provided, fixed_bounds 
            specifies the bounds to work with.
            The purpose of this latter option is to allow the user to compute 
            matching distances with uniform precision over a large collection of 2-D 
            persistence modules, which may exhibit features at different scales.
    """
    # First, use fixed_bounds to set the upper right corner and lower-left
    # corner to be considered.
    if fixed_bounds is None:
        # otherwise, determine bounds from the bounds of the two modules
        bounds1 = rivet.bounds(module1)
        bounds2 = rivet.bounds(module2)
        fixed_bounds = common_bounds(bounds1, bounds2)
    LL = fixed_bounds.lower
    UR = fixed_bounds.upper
    UL = [LL[0], UR[1]]
    LR = [UR[0], LL[1]]
    # print("LL", LL)
    # print("UR", UR)
    # Now we build up a list of the lines we consider in computing the matching distance.
    # Each line is given as a (slope,offset) pair.
    lines = generate_lines(grid_size, UL, LR)



    # next, for each of the two 2-D persistence modules, get the barcode
    # associated to the list of lines.
    multi_bars1 = rivet.barcodes(module1, lines)
    multi_bars2 = rivet.barcodes(module2, lines)

    # first compute the unweighted distance between the pairs
    raw_distances = hera.multi_bottleneck_distance(
        [bars for (_, bars) in multi_bars1],
        [bars for (_, bars) in multi_bars2]
    )

    return calculate_match(zip(lines, raw_distances), normalize, LL, UR)


def generate_lines(grid_size, UL, LR):
    lines = []
    for i in range(grid_size):
        # We will choose `grid_parameter` slopes between 0 and 90;
        # we do not however consider the values 0 and 90, since in view of stability considerations
        # these are not considered in the definition of the matching distance.
        slope = 90 * (i + 1) / (grid_size + 1)

        # find the offset parameters such that the lines with slope slope just
        # touches the upper left corner of the box
        UL_offset = find_offset(slope, UL)
        LR_offset = find_offset(slope, LR)

        # Choose the values of offset for this particular choice of slope.
        if grid_size == 1:
            lines.append((slope, UL_offset - LR_offset))
        # largest and smallest offsets specify lines that touch
        # the upper left and lower right corners of the rectangular region of
        # interest.
        else:
            for j in range(grid_size):
                offset = LR_offset + j * \
                                     (UL_offset - LR_offset) / (grid_size - 1)
                lines.append((slope, offset))
    return lines


def calculate_match(line_distances, normalize, LL, UR):
    # now compute matching distance
    m_dist = 0

    for (slope, _), raw_distance in line_distances:
        # To determine the weight to use for the line given by (slope,offset),
        # we need to take into account both the weight coming from slope of
        # the line, and also the normalization, which changes both the effective
        # weight and the effective bottleneck distance.

        # first, let's recall how the re-weighting works in the un-normalized case.
        # According to the definition of the matching distance, we choose
        # the weight so that if the interleaving distance between Mod1 and Mod2
        # is 1, then the weighted bottleneck distance between the slices is at most 1.

        m = np.tan(np.radians(slope))

        if not normalize:
            q = max(m, 1 / m)
            w = 1 / np.sqrt(1 + q**2)
            m_dist = max(m_dist, w * raw_distance)

        else:
            # next, let's consider the normalized case. If the un-normalized slope
            # is `slope`, then the normalized slope is given as follows
            delta_x = UR[0] - LL[0]
            delta_y = UR[1] - LL[1]
            if delta_y == 0:
                print(
                    'corner case where delta_y=0 not addressed.  expect a divide-by-0 problem')
            mn = m * delta_x / delta_y

            # so the associated weight in the normalized case is given by
            q = max(mn, 1 / mn)
            w = 1 / np.sqrt(1 + q**2)

            # of course, this code can be made more compact, but hopefully this
            # way is readable

            # moreover, normalization changes the length of a line segment along the line (slope,offset),
            # and hence also the bottleneck distance, by a factor of
            bottleneck_stretch = np.sqrt(
                ((m / delta_y)**2 + (1 / delta_x)**2) / (m**2 + 1))
            m_dist = max(m_dist, w * raw_distance * bottleneck_stretch)

    return m_dist

