# Borrowed from https://github.com/IntelPNI/brainiak-extras
import os
import tempfile

from atlatl import rivet, hera, barcode, Matching_Distance

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


# def test_point_cloud_1():
#     barcodes = barcode.Barcode([
#         barcode.Bar(0, 1, 3),
#         barcode.Bar(0, inf, 1)
#     ])
#     assert_barcodes(cloud_1, 0, 0, 0, 0, barcodes=barcodes)

prism_1 ="""
bifiltration
x-axis label
y-axis label
0 1 1 0
0 2 1 0
1 2 1 0

3 4 0 1
4 5 0 1
3 5 0 1

1 2 4 1 1
2 4 5 1 1
0 1 3 1 1
1 3 4 1 1
0 2 5 1 1

0 3 5 1 1
0 1 2 4 0 
3 4 5 0 4

"""

prism_2 = """
bifiltration
x-axis label
y-axis label

1 2 4 0 0
2 4 5 0 0
0 1 3 0 0
1 3 4 0 0
0 2 5 0 0

0 3 5 0 0 

0 1 2 3 3
"""

def test_overlaps():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, 'mod1'), 'w') as f:
            f.write(prism_1)

        with open(os.path.join(tempdir, 'mod2'), 'w') as f:
            f.write(prism_2)

        pre1 = rivet.compute_file(os.path.join(tempdir, "mod1"))
        mod1 = open(pre1, 'rb').read()
        pre2 = rivet.compute_file(os.path.join(tempdir, "mod2"))
        mod2 = open(pre2, 'rb').read()
        bounds1 = rivet.bounds(mod1)
        print(bounds1)
        bounds2 = rivet.bounds(mod2)
        print(bounds2)
        dist = Matching_Distance.matching_distance(mod1, mod2, 11, False, [])

        assert dist == 1, dist
