# -*- coding: utf-8 -*-
#
"""setuptools-based setup.py template for Cython projects.

Setup for local modules in this directory, that are not installed as part of
the library.

Note: This is essentially a stripped down version of the setup.py template
in the top level directory, adapted to facilitate the build_ext --inplace
required to build the cython module being tested.

Supports Python 2.7 and 3.4.

Usage:
    python setup.py build_ext --inplace
"""

from __future__ import division, print_function, absolute_import

try:
    # Python 3
    MyFileNotFoundError = FileNotFoundError
except:  # FileNotFoundError does not exist in Python 2.7
    # Python 2.7
    # - open() raises IOError
    # - remove() (not currently used here) raises OSError
    MyFileNotFoundError = (IOError, OSError)

#########################################################
# General config
#########################################################


#########################################################
# Init
#########################################################

# check for Python 2.7 or later
# http://stackoverflow.com/questions/19534896/enforcing-python-version-in-setup-py
import sys
if sys.version_info < (2,7):
    sys.exit('Sorry, Python < 2.7 is not supported')

import os

from setuptools import setup
from setuptools.extension import Extension

# Cython installed? Must be imported after setuptools Extension...
# ...and we insist on being able to load because we're testing some
# Cython functionality.
#
from Cython.Build import cythonize


#########################################################
# Definitions
#########################################################

# Define our base set of compiler and linker flags.
#
# This is geared toward x86_64, see
#    https://gcc.gnu.org/onlinedocs/gcc-4.6.4/gcc/i386-and-x86_002d64-Options.html
#
# Customize these as needed.
#
# Note that -O3 may sometimes cause mysterious problems, so we limit ourselves to -O2.

extra_compile_args = ['-O2']
extra_compile_args = ['-O0', '-g']
extra_link_args    = []
extra_link_args    = []

# Additional flags to compile/link with OpenMP
#
openmp_compile_args = ['-fopenmp']
openmp_link_args    = ['-fopenmp']


#########################################################
# Helpers
#########################################################

# Make absolute cimports work.
#
# See
#     https://github.com/cython/cython/wiki/PackageHierarchy
#
my_include_dirs = ["."]


# Wrapper to create (Cython-based) extensions
#
# FIXME: Add libraries - also from a setup.cfg file?
# FIXME: Add arbitrary source code / C files in addition to the main cython .pyx
def declare_extension(extName, openmp = False, include_dirs = None):
    """Declare a Cython extension module for setuptools.

Parameters:
    extName : str
        Absolute module name, e.g. use `mylibrary.mypackage.mymodule`
        for the Cython source file `mylibrary/mypackage/mymodule.pyx`.

    openmp : bool
        If True, compile and link with OpenMP.

Return value:
    Extension object
        that can be passed to ``setuptools.setup``.
"""
    extPath = extName.replace(".", os.path.sep) + ".pyx"

    compile_args = list(extra_compile_args) # copy
    link_args    = list(extra_link_args)
    libraries    = ["m"]  # link libm; this is a list of library names without the "lib" prefix

    # OpenMP
    if openmp:
        compile_args.insert( 0, openmp_compile_args )
        link_args.insert( 0, openmp_link_args )

    # See
    #    http://docs.cython.org/src/tutorial/external.html
    #
    # on linking libraries to your Cython extensions.
    #
    return Extension( extName,
                      [extPath],
                      extra_compile_args = compile_args,
                      extra_link_args    = link_args,
                      include_dirs       = include_dirs,
                      libraries          = libraries
                    )


# Clean command (from https://stackoverflow.com/a/1712544)
#
from setuptools import Command # or distutils.core?
import os, sys

class CleanCommand(Command):
    description = "clean after a build, forcefully removing dist/build and .egg-info directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, "Must be in package root: %s" % self.cwd
        os.system("rm -rfv ./build ./dist ./*.egg-info ./__pycache_ *.so *.c")


cmdclass = {"clean": CleanCommand}


#########################################################
# Set up modules
#########################################################

# Declare Cython extension modules
#
ext_module_cythonmodule = declare_extension("cython_module", openmp = False)

# This is mainly to allow a manual logical ordering of the declared modules
#
ext_modules = [ext_module_cythonmodule]

# ...and cythonize (if needed)
#
ext_modules = cythonize(ext_modules)


#########################################################
# Call setup()
#########################################################

setup(
    # See
    #    http://setuptools.readthedocs.io/en/latest/setuptools.html
    #
    setup_requires = ["cython", "numpy"],
    install_requires = ["numpy"],

    # All extension modules (list of Extension objects)
    #
    ext_modules = ext_modules,

    # Custom commands
    #
    cmdclass = cmdclass
)
