from . import barcode
import subprocess
import shlex
import fractions
import tempfile
import os


"""An interface for rivet_console, using the command line
and subprocesses."""

rivet_executable = 'rivet_console'


class Point:
    def __init__(self, appearance, *coords):
        self.appearance = appearance
        self.coords = coords

    @property
    def dimension(self):
        return len(self.coords)


class PointCloud:
    def __init__(self, points, second_param_name,
                 comments=None, max_dist=None):
        self.points = points
        self.comments = comments
        self.dimension = points[0].dimension
        self.second_param_name = second_param_name
        for i, p in enumerate(points):
            if p.dimension != self.dimension:
                raise ValueError("Expected points of dimension %d,"
                                 " but point at position %d has dimension %d"
                                 % (self.dimension, i, p.dimension))
        self.max_dist = max_dist or self._calc_max_dist()

    def _calc_max_dist(self):
        # Simplest possible max distance measure
        lo, hi = 0, 0
        for p in self.points:
            for coord in p.coords:
                if coord < lo:
                    lo = coord
                if coord > hi:
                    hi = coord
        return abs(hi - lo)

    def save(self, out):
        if self.comments:
            out.writelines(["# " + line + "\n"
                            for line in str(self.comments).split("\n")])
        out.write("points\n")
        out.write(str(self.dimension) + "\n")
        out.write(str(self.max_dist) + "\n")
        out.write(self.second_param_name + "\n")
        for p in self.points:
            for c in p.coords:
                out.write(str(c))
                out.write(" ")
            out.write(str(p.appearance))
            out.write("\n")
        out.write("\n")


class Bifiltration:
    def __init__(self, x_label, y_label, points):
        self.x_label = x_label
        self.y_label = y_label
        self.points = points
        for p in self.points:
            if not hasattr(p.appearance, '__len__') or len(p.appearance) != 2:
                raise ValueError(
                    "For a bifiltration, points must have a 2-tuple in the appearance field")

    def save(self, out):
        out.write('bifiltration\n')
        out.write(self.x_label + '\n')
        out.write(self.y_label + '\n')
        for p in self.points:
            for c in p.coords:
                out.write(str(c))
                out.write(" ")
            for b in p.appearance:
                out.write(str(b))
                out.write(" ")
            out.write("\n")
        out.write("\n")


def compute_point_cloud(cloud, homology=0, x=0, y=0, verify=False):
    with tempfile.TemporaryDirectory() as dir:
        cloud_file_name = os.path.join(dir, 'points.txt')
        with open(cloud_file_name, 'w+t') as cloud_file:
            cloud.save(cloud_file)
        output_name = compute_file(cloud_file_name,
                                   homology=homology, x=x, y=y)
        with open(output_name, 'rb') as output_file:
            output = output_file.read()
        if verify:
            assert bounds(output)
        return output


def compute_bifiltration(bifiltration, homology=0, verify=False):
    with tempfile.TemporaryDirectory() as dir:
        bifiltration_name = os.path.join(dir, 'points.txt')
        with open(bifiltration_name, 'w+t') as bifiltration_file:
            bifiltration.save(bifiltration_file)
        output_name = compute_file(bifiltration_name,
                                   homology=homology)
        with open(output_name, 'rb') as output_file:
            output = output_file.read()
        if verify:
            assert bounds(output)
        return output


def barcodes(bytes, slices):
    """Returns a Barcode for each (angle, offset) tuple in `slices`."""
    with tempfile.TemporaryDirectory() as dir:
        with open(os.path.join(dir, 'precomputed.rivet'), 'wb') as precomp:
            precomp.write(bytes)
        with open(os.path.join(dir, 'slices.txt'), 'wt') as slice_temp:
            for angle, offset in slices:
                slice_temp.write("%s %s\n" % (angle, offset))
        return barcodes_file(precomp.name, slice_temp.name)


def _rivet_name(base, homology, x, y):
    output_name = base + (".H%d_x%d_y%d.rivet" % (homology, x, y))
    return output_name


def compute_file(name, output_name=None, homology=0, x=0, y=0):
    if not output_name:
        output_name = _rivet_name(name, homology, x, y)
    cmd = "%s %s %s -H %d -x %d -y %d" % \
          (rivet_executable, name, output_name, homology, x, y)
    if not subprocess.check_call(shlex.split(cmd)):
        return output_name


def barcodes_file(name, slice_name):
    cmd = "%s %s --barcodes %s" % (rivet_executable, name, slice_name)
    return _parse_slices(
        subprocess.check_output(
            shlex.split(cmd)).split(b'\n'))


def betti_file(name, x=0, y=0):
    cmd = "%s %s --betti -x %d -y %d" % (rivet_executable, name, x, y)
    return _parse_betti(subprocess.check_output(shlex.split(cmd)).split(b'\n'))


def bounds_file(name):
    cmd = "%s %s --bounds" % (rivet_executable, name)
    return parse_bounds(subprocess.check_output(shlex.split(cmd)).split(b'\n'))


def bounds(bytes):
    assert len(bytes) > 0
    with tempfile.TemporaryDirectory() as dir:
        precomp_name = os.path.join(dir, 'precomp.rivet')
        with open(precomp_name, 'wb') as precomp:
            precomp.write(bytes)
        return bounds_file(precomp_name)


class Bounds:
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return "Bounds(%s, %s)" % (self.lower, self.upper)


def parse_bounds(lines):
    low = (0, 0)
    high = (0, 0)
    for line in lines:
        line = str(line, 'utf-8')
        line = line.strip()
        if line.startswith('low:'):
            parts = line[5:].split(",")
            low = tuple(map(float, parts))
        if line.startswith('high:'):
            parts = line[6:].split(",")
            high = tuple(map(float, parts))
    return Bounds(low, high)


class Dimensions:
    def __init__(self, x_grades, y_grades, ):
        self.x_grades = x_grades
        self.y_grades = y_grades

    def __repr__(self):
        return "Dimensions(%s, %s)" % (self.x_grades, self.y_grades)

    def __eq__(self, other):
        return isinstance(other, Dimensions) \
            and self.x_grades == other.x_grades \
            and self.y_grades == other.y_grades


class MultiBetti:
    def __init__(self, dims, xi_0, xi_1, xi_2):
        self.dimensions = dims
        self.xi_0 = xi_0,
        self.xi_1 = xi_1,
        self.xi_2 = xi_2

    def __repr__(self):
        return "MultiBetti(%s, %s, %s, %s)" % \
               (self.dimensions, self.xi_0, self.xi_1, self.xi_2)


def _parse_betti(text):
    x_grades = []
    y_grades = []
    current_grades = None
    xi = [[], [], []]

    current_xi = None

    for line in text:
        line = line.strip()
        if len(line) == 0:
            line = None
        else:
            line = str(line, 'utf-8')
        if line == 'x-grades':
            current_grades = x_grades
        elif line == 'y-grades':
            current_grades = y_grades
        elif line is None:
            current_grades = None
            current_xi = None
        elif current_grades is not None:
            current_grades.append(fractions.Fraction(line))
        elif line.startswith('xi_'):
            current_xi = xi[int(line[3])]
        elif current_xi is not None:
            current_xi.append(tuple(map(int, line[1:-1].split(','))))

    return MultiBetti(Dimensions(x_grades, y_grades), *xi)


def _parse_slices(text):
    slices = []
    for line in text:
        line = line.strip()
        if not line:
            continue
        header, body = line.split(b':')
        angle, offset = header.split(b' ')
        bars = []
        for part in body.split(b','):
            part = part.strip()
            if not part:
                continue
            birth, death, mult = part.split(b' ')
            bars.append(barcode.Bar(float(birth), float(death), int(mult[1:])))

        code = barcode.Barcode(bars)
        slices.append(((float(angle), float(offset)), code))
    return slices
