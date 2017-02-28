# Borrowed from https://github.com/IntelPNI/brainiak-extras
from atlatl import rivet, hera, barcode

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

