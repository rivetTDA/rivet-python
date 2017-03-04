from . import barcode
import typecheck as tc
import subprocess
import tempfile
import os


# note we use a constant instead of inf because of a bug in bottleneck_dist.
@tc.typecheck
def bottleneck_distance(left: barcode.Barcode,
                        right: barcode.Barcode,
                        inf: float=1e10,
                        cap: int=10,
                        relative_error=1e-10 # Needed to keep hera from crashing, which it does on some inputs with
                                             # default relative_error. This default value is high enough to prevent it.
                        ):
    # Hera crashes when one or both barcodes are empty
    if len(left.bars) == 0 or len(right.bars) == 0:
        if len(left.bars) == 0 and len(right.bars) == 0:
            return 0
        return cap
    else:
        with tempfile.TemporaryDirectory() as temp:
            t1_name = os.path.join(temp, 'self.txt')
            t2_name = os.path.join(temp, 'other.txt')
            with open(t1_name, 'wt') as t1:
                for bar in left.bars:
                    t1.writelines(["%s %s\n" %
                                   (bar.start, min(inf, bar.end))
                                   for _ in range(bar.multiplicity)])
            with open(t2_name, 'wt') as t2:
                for bar in right.bars:
                    t2.writelines(["%s %s\n" %
                                   (bar.start, min(inf, bar.end))
                                   for _ in range(bar.multiplicity)])
            dist = subprocess.check_output(["bottleneck_dist", t1_name, t2_name, str(relative_error)])
            # print("Distance: ", dist)
            return min(cap, float(dist))
