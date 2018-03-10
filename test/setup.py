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

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

from __future__ import division, print_function, absolute_import

import os
import sys

from setuptools           import setup
from setuptools           import Command
from setuptools.extension import Extension

if sys.version_info < (2,7):
    sys.exit('Sorry, Python < 2.7 is not supported')


#-------------------------------------------------------------------------------
# Configuration options
#-------------------------------------------------------------------------------

# Note: By default, the same compiler and linker options are used as for building
# Python. In this section, *additional* options can be specified.
#
# In addition, absolute cimports in Cython require to include "." in include_dirs
# (see https://github.com/cython/cython/wiki/PackageHierarchy)

include_dirs = ["."]

# Additional libraries; always include libmath

libraries = ["m"]


#-------------------------------------------------------------------------------
# Helpers
#-------------------------------------------------------------------------------

# Clean command (from https://stackoverflow.com/a/1712544)

class CleanCommand(Command):
    description = "clean after a build, forcefully removing dist/build and .egg-info directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, "Must be in package root: %s" % self.cwd
        os.system("rm -rfv ./build ./dist ./*.egg-info ./.pytest_cache ./__pycache__ *.so")


# Cythonise command

class CythonizeCommand(Command):
    description  = "run cython on the cython-based extensions"
    user_options = []
    ext_modules  = None
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        from Cython.Build import cythonize
        if self.ext_modules is not None:
            dummy = cythonize(self.ext_modules)
        else:
            print("WARNING: Nothing found to cythonize...")

cmdclass = {"clean": CleanCommand,
            "cython": CythonizeCommand,
            "cythonise": CythonizeCommand,
            "cythonize": CythonizeCommand
           }


#-------------------------------------------------------------------------------
# Set up extension / cython modules
#-------------------------------------------------------------------------------

# Declare Cython extension modules

ext_modules = [Extension("cython_module",
                         ["cython_module.pyx"],
                         include_dirs = include_dirs,
                         libraries    = libraries)
              ]


#########################################################
# Call setup()
#########################################################

setup(
    # See http://setuptools.readthedocs.io/en/latest/setuptools.html

    setup_requires   = ["setuptools>=18.0", "numpy", "pytest-runner"],
    install_requires = ["numpy"],

    # All extension modules (list of Extension objects)

    ext_modules = ext_modules,

    # Custom commands

    cmdclass = cmdclass
)
