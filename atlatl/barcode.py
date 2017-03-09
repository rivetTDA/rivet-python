import numpy as np

"""
Standard bar code classes that can be shared among
the wrappers for multiple tools
"""


class Bar(object):
    """A single bar, which should be contained in a Barcode"""

    def __init__(self, start, end, multiplicity):
        """Constructor. Takes start/birth, end/death, and multiplicity."""
        self.start = start
        self.end = end
        self.multiplicity = multiplicity

    def __repr__(self):
        return "Bar(%f, %f, %d)" % (self.start, self.end, self.multiplicity)

    def expand(self):
        """Returns self.multiplicity copies of this bar,
        all with multiplicity 1"""
        return [Bar(self.start, self.end, 1)] * self.multiplicity

    def to_array(self):
        return np.array([self.start, self.end])


class Barcode(object):
    """A collection of bars"""
    def __init__(self, bars=None):
        if bars is None:
            bars = []
        self.bars = bars

    def __repr__(self):
        return "Barcode(%s)" % self.bars

    def to_array(self):
        """Returns a numpy array [[start1, end1], [start2,end2]...].
        Note that all bars are expanded, so the same start, end may
        occur multiple times."""
        return np.hstack(tuple([b.to_array() for bar in self.bars
                                for b in bar.expand()])) \
            .reshape(len(self.bars), 2).transpose()
