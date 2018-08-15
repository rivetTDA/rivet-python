
from setuptools import setup, find_packages
import os
import sys

assert sys.version_info >= (3, 4), (
    "Please use Python version 3.4 or higher, "
    "lower versions are not supported"
)

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

ext_modules = [
]

# As of Python 3.6, CCompiler has a `has_flag` method.
setup(
    name='pyrivet',
    use_scm_version=True,
    setup_requires=[
        'numpy',
        'setuptools_scm',
    ],
    install_requires=[
        'numpy',
    ],
    author='The RIVET developers',
    author_email='xoltar@xoltar.org',
    url='https://github.com/rivettda/rivet-python',
    description='Python interface to RIVET (Rank Invariant Visualization and Exploration Tool)',
    license='BSD-3',
    keywords='topology, algebraic topology, topological data analysis',
    long_description=long_description,
    ext_modules=ext_modules,
    # cmdclass={'build_ext': BuildExt},
    packages=find_packages(),
    python_requires='>=3.4',
    zip_safe=False,
)
