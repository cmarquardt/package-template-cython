# -*- coding: utf-8 -*-
#
"""setuptools-based package template for Cython projects.

Main setup for the library.

Supports Python 2.7 as well as 3.4 and higher.

Usage as usual with setuptools:
    python setup.py build_ext
    python setup.py build
    python setup.py install
    python setup.py sdist

and also
    python setup.py cython

For details, see
    http://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference
or
    python setup.py --help
    python setup.py --help-commands
    python setup.py --help bdist_wheel  # or any command

For configuring build and linker options, the following environment variables
honored:

    CFLAGS
    LDFLAGS
    LIBS

Corresponding variables in setup.cfg are read during configuration and overwrite
environment variables.

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
# Package information
#-------------------------------------------------------------------------------

# Name of the top-level package of your library.

libname="mylibrary"

# Short description for package list on PyPI

SHORTDESC="setuptools package template for Cython projects"

# Long description for package homepage on PyPI

DESC="""setuptools-based package template for Cython projects.

The focus of this template is on numerical scientific projects,
where a custom Cython extension (containing all-new code) can
bring a large speedup.

For completeness, a minimal Cython module is included.

Supports Python 2.7 and 3.4.

"""

#-------------------------------------------------------------------------------
# Configuration options
#-------------------------------------------------------------------------------

# Note: By default, the same compiler and linker options are used as for building
# Python. In this section, *additional* options can be specified.
#
# In addition, absolute cimports in Cython require to include "." in include_dirs
# (see https://github.com/cython/cython/wiki/PackageHierarchy)

include_dirs = ["."]
#include_dirs = [".", np.get_include()]

# Additional compiler and linker flags

cflags  = []
ldflags = []

# Additional libraries; always include libmath

libraries = ["m"]


#-------------------------------------------------------------------------------
# Helpers
#-------------------------------------------------------------------------------

# Automatic versioning based on https://github.com/cmarquardt/miniver2:

def get_version_and_cmdclass(package_name):
    try: # Python 3
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location('version',
                                       os.path.join(package_name, "_version.py"))
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.__version__, module.cmdclass
    except: # Python 2
        import imp
        module = imp.load_source(package_name.split('.')[-1], os.path.join(package_name, "_version.py"))
        return module.__version__, module.cmdclass

version, ver_cmdclass = get_version_and_cmdclass('mylibrary')


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
        os.system("rm -rfv ./build ./dist ./*.egg-info ./.pytest_cache")


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

# Join our own and miniver's cmdclass disctionaries

cmdclass.update(ver_cmdclass)


#-------------------------------------------------------------------------------
# Files in the distribution
#-------------------------------------------------------------------------------

# Set up data files for packaging.
#
# Directories (relative to the top-level directory where setup.py resides) in which to look for data files.

datadirs  = ("test",)

# File extensions to be considered as data files. (Literal, no wildcards.)

dataexts  = (".py",  ".pyx", ".pxd",  ".c", ".cpp", ".h",  ".sh",  ".lyx", ".tex", ".txt", ".pdf")

# Standard documentation to detect (and package if it exists).

standard_docs     = ["README", "LICENSE", "TODO", "CHANGELOG", "AUTHORS"]  # just the basename without file extension
standard_doc_exts = [".md", ".rst", ".txt", ""]  # commonly .md for GitHub projects, but other projects may use .rst or .txt (or even blank).

# Gather user-defined data files
#
# http://stackoverflow.com/questions/13628979/setuptools-how-to-make-package-contain-extra-data-folder-and-all-folders-inside

datafiles = []
getext = lambda filename: os.path.splitext(filename)[1]
for datadir in datadirs:
    datafiles.extend( [(root, [os.path.join(root, f) for f in files if getext(f) in dataexts])
                       for root, dirs, files in os.walk(datadir)] )


# Add standard documentation (README et al.), if any, to data files

detected_docs = []
for docname in standard_docs:
    for ext in standard_doc_exts:
        filename = "".join( (docname, ext) )  # relative to the directory in which setup.py resides
        if os.path.isfile(filename):
            detected_docs.append(filename)
datafiles.append( ('.', detected_docs) )


#-------------------------------------------------------------------------------
# Set up extension / cython modules
#-------------------------------------------------------------------------------

# Declare Cython extension modules

ext_modules = []
ext_modules.append(Extension("mylibrary.dostuff",
                             ["mylibrary/dostuff.pyx"],
                             extra_compile_args = cflags,
                             extra_link_args    = ldflags,
                             include_dirs       = include_dirs,
                             libraries          = libraries)
                   )

ext_modules.append(Extension("mylibrary.compute",
                             ["mylibrary/compute.pyx"],
                             extra_compile_args = cflags,
                             extra_link_args    = ldflags,
                             include_dirs       = include_dirs,
                             libraries          = libraries)
                   )

ext_modules.append(Extension("mylibrary.subpackage.helloworld",
                             ["mylibrary/subpackage/helloworld.pyx"],
                             extra_compile_args = cflags,
                             extra_link_args    = ldflags,
                             include_dirs       = include_dirs,
                             libraries          = libraries)
                   )

# Register extensions with the cythonize command

CythonizeCommand.ext_modules = ext_modules


#-------------------------------------------------------------------------------
# Call setup()
#-------------------------------------------------------------------------------

setup(
    name             = "package-template-cython",
    version          = version,
    author           = "Christian Marquardt",
    author_email     = "christian@marquardt.sc",
    url              = "https://github.com/cmarquardt/package-template-cython",
    provides         = ["package_template_cython"],
    description      = SHORTDESC,
    long_description = DESC,

    # Keywords for PyPI (in case you upload your project)
    #
    # e.g. the keywords your project uses as topics on GitHub, minus "python" (if there)

    keywords         = ["setuptools package template example cython"],

    # CHANGE THIS
    license          = "Unlicense",

    # free-form text field; http://stackoverflow.com/questions/34994130/what-platforms-argument-to-setup-in-setup-py-does
    platforms        = ["Linux", "MacOS X"],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers for the standard classifiers

    classifiers = [ "Development Status :: 4 - Beta",
                    "Environment :: Console",
                    "Intended Audience :: Developers",
                    "Intended Audience :: Science/Research",
                    "License :: Unlicense",  # not a standard classifier; CHANGE THIS
                    "Operating System :: POSIX :: Linux",
                    "Operating System :: MacOS :: MacOS X",
                    "Programming Language :: Cython",
                    "Programming Language :: Python",
                    "Topic :: Scientific/Engineering",
                    "Topic :: Scientific/Engineering :: Mathematics",
                    "Topic :: Software Development :: Libraries",
                    "Topic :: Software Development :: Libraries :: Python Modules"
                  ],

    # See http://setuptools.readthedocs.io/en/latest/setuptools.html

    setup_requires   = ["setuptools>=18.0", "numpy", "pytest-runner"],
    install_requires = ["numpy"],

    # All extension modules (list of Extension objects)

    ext_modules = ext_modules,

    # Declare packages so that  python -m setup build  will copy .py files (especially __init__.py).

    # Note: This **does not** automatically recurse into subpackages, so they must also be declared.

    packages = ["mylibrary", "mylibrary.subpackage"],

    # Install also Cython headers and C source files so that other Cython modules can cimport ours

    # Note: Empty key = all modules
    package_data = {"" : ["*.pyx", "*.pxd", "*.c", "*.h"]},

    # Custom data files not inside a Python package

    data_files = datafiles,

    # Custom commands

    cmdclass = cmdclass,

    # Disable zip_safe, because:
    #   - Cython won't find .pxd files inside installed .egg, hard to compile libs depending on this one
    #   - dynamic loader may need to have the library unzipped to a temporary directory anyway (at import time)

    zip_safe = False
)
