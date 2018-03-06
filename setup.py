# -*- coding: utf-8 -*-
#
"""setuptools-based package template for Cython projects.

Main setup for the library.

Supports Python 2.7 and 3.4.

Usage as usual with setuptools:
    python setup.py build_ext
    python setup.py build
    python setup.py install
    python setup.py sdist

For details, see
    http://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference
or
    python setup.py --help
    python setup.py --help-commands
    python setup.py --help bdist_wheel  # or any command
"""

from __future__ import division, print_function, absolute_import

# Python 3 vs python 2
#
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

# Name of the top-level package of your library.
#
# This is also the top level of its source tree, relative to the top-level project directory setup.py resides in.
#
libname="mylibrary"

# Short description for package list on PyPI
#
SHORTDESC="setuptools package template for Cython projects"

# Long description for package homepage on PyPI
#
DESC="""setuptools-based package template for Cython projects.

The focus of this template is on numerical scientific projects,
where a custom Cython extension (containing all-new code) can
bring a large speedup.

For completeness, a minimal Cython module is included.

Supports Python 2.7 and 3.4.
"""

# Set up data files for packaging.
#
# Directories (relative to the top-level directory where setup.py resides) in which to look for data files.
datadirs  = ("test",)

# File extensions to be considered as data files. (Literal, no wildcards.)
dataexts  = (".py",  ".pyx", ".pxd",  ".c", ".cpp", ".h",  ".sh",  ".lyx", ".tex", ".txt", ".pdf")

# Standard documentation to detect (and package if it exists).
#
standard_docs     = ["README", "LICENSE", "TODO", "CHANGELOG", "AUTHORS"]  # just the basename without file extension
standard_doc_exts = [".md", ".rst", ".txt", ""]  # commonly .md for GitHub projects, but other projects may use .rst or .txt (or even blank).


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
#
try:
    # Cython
    from Cython.Build import cythonize
    use_cython = True
except: # Cython not found; just use C sources
    use_cython = False


#########################################################
# Definitions
#########################################################

# FIXME: This should be replaced by properly supporting a setup.cfg file

# Define our base set of compiler and linker flags.
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
# For example: my_include_dirs = [np.get_include()]
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


# Gather user-defined data files
#
# http://stackoverflow.com/questions/13628979/setuptools-how-to-make-package-contain-extra-data-folder-and-all-folders-inside
#
datafiles = []
getext = lambda filename: os.path.splitext(filename)[1]
for datadir in datadirs:
    datafiles.extend( [(root, [os.path.join(root, f) for f in files if getext(f) in dataexts])
                       for root, dirs, files in os.walk(datadir)] )


# Add standard documentation (README et al.), if any, to data files
#
detected_docs = []
for docname in standard_docs:
    for ext in standard_doc_exts:
        filename = "".join( (docname, ext) )  # relative to the directory in which setup.py resides
        if os.path.isfile(filename):
            detected_docs.append(filename)
datafiles.append( ('.', detected_docs) )


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
        os.system("rm -rfv ./build ./dist ./*.egg-info")


# Cythonise command
#
class CythonizeCommand(Command):
    description  = "run cython on the cython-based extensions"
    user_options = []
    extensions   = None
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        from Cython.Build import cythonize
        if self.extensions is not None:
            dummy = cythonize(self.extensions)
        else:
            print("WARNING: Nothing found to cythonize...")

cmdclass = {"clean": CleanCommand,
            "cython": CythonizeCommand,
            "cythonise": CythonizeCommand,
            "cythonize": CythonizeCommand
           }

# Extract __version__ from the package __init__.py
# (since it's not a good idea to actually run __init__.py during the build process).
#
# http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
#
#import ast
#init_py_path = os.path.join(libname, '__init__.py')
#version = '0.0.unknown'
#try:
#    with open(init_py_path) as f:
#        for line in f:
#            if line.startswith('__version__'):
#                version = ast.parse(line).body[0].value.s
#                break
#        else:
#            print( "WARNING: Version information not found in '%s', using placeholder '%s'" % (init_py_path, version), file = sys.stderr )
#except MyFileNotFoundError:
#    print( "WARNING: Could not find file '%s', using placeholder version information '%s'" % (init_py_path, version), file = sys.stderr )

# Automatic versioning based on https://github.com/jbweston/miniver:
#
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

# Join our own and miniver's cmdclass disctionaries
cmdclass.update(ver_cmdclass) # Add ver_cmdclass to cmdclass; not ver_cmdclass would take precedence in case of overlappingkeys


#########################################################
# Set up modules
#########################################################

# Declare Cython extension modules
#
ext_module_dostuff    = declare_extension( "mylibrary.dostuff",               openmp = False , include_dirs = my_include_dirs )
ext_module_compute    = declare_extension( "mylibrary.compute",               openmp = False , include_dirs = my_include_dirs )
ext_module_helloworld = declare_extension( "mylibrary.subpackage.helloworld", openmp = False , include_dirs = my_include_dirs )

# This is mainly to allow a manual logical ordering of the declared modules
#
ext_modules = [ext_module_dostuff,
               ext_module_compute,
               ext_module_helloworld]

# Also support setup.ps's cython command (which requires the extensions)
#
CythonizeCommand.extensions = ext_modules

# ...and cythonize (if needed)
#
if use_cython:
    ext_modules = cythonize(ext_modules)


#########################################################
# Call setup()
#########################################################

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
    #
    keywords         = ["setuptools package template example cython"],

    # CHANGE THIS
    license          = "Unlicense",

    # free-form text field; http://stackoverflow.com/questions/34994130/what-platforms-argument-to-setup-in-setup-py-does
    platforms        = ["Linux", "MacOS X"],

    # See
    #    https://pypi.python.org/pypi?%3Aaction=list_classifiers
    #
    # for the standard classifiers.
    #
    # Remember to configure these appropriately for your project, especially license!
    #
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

    # See
    #    http://setuptools.readthedocs.io/en/latest/setuptools.html
    #
    setup_requires   = ["setuptools>=18.0",
                        "numpy"],
    install_requires = ["numpy"],

    # All extension modules (list of Extension objects)
    #
    ext_modules = ext_modules,

    # Declare packages so that  python -m setup build  will copy .py files (especially __init__.py).
    #
    # This **does not** automatically recurse into subpackages, so they must also be declared.
    #
    packages = ["mylibrary", "mylibrary.subpackage"],

    # Install also Cython headers so that other Cython modules can cimport ours
    #
    # Fileglobs relative to each package, **does not** automatically recurse into subpackages.
    #
    # FIXME: force sdist, but sdist only, to keep the .pyx files (this puts them also in the bdist)
    package_data={'mylibrary': ['*.pxd', '*.pyx'],
                  'mylibrary.subpackage': ['*.pxd', '*.pyx']},

    # Disable zip_safe, because:
    #   - Cython won't find .pxd files inside installed .egg, hard to compile libs depending on this one
    #   - dynamic loader may need to have the library unzipped to a temporary directory anyway (at import time)
    #
    zip_safe = False,

    # Custom data files not inside a Python package
    #
    data_files = datafiles,

    # Custom commands
    #
    cmdclass = cmdclass
)
