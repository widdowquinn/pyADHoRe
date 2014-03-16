# try using distribute or setuptools or distutils.
try:
    import distribute_setup
    distribute_setup.use_setuptools()
except:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import sys
import re

# parse version from package/module without importing or evaluating the code
with open('pyADHoRe/iadhore.py') as fh:
    for line in fh:
        m = re.search(r"^__version__ = '(?P<version>[^']+)'$", line)
        if m:
            version = m.group('version')
            break

if sys.version_info <= (2, 5):
    sys.stderr.write("ERROR: pyADHoRe requires Python Version 2.6 or above...exiting.\n")
    sys.exit(1)

setup(
    name = "pyADHoRe",
    version = version,
    author = "Leighton Pritchard",
    author_email = "leighton.pritchard@hutton.ac.uk",
    description = "pyADHoRe provides a data structure for import and manipulation of i-ADHoRe output.",
    license = "GPLv3",
    keywords = "genome ortholog synteny i-ADHoRe",
    platforms = "Posix; MacOS X",
    url = "https://github.com/widdowquinn/pyADHoRe",   # project home page, if any
    download_url = "",
    scripts = [],
    packages = ['pyADHoRe'],
    install_requires = ['networkx>=1.8.1'],
    package_data = {
        'pyADHoRe': [],
        },
    test_suite='tests.test_search.TestSearch',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GPLv3 License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
    )
