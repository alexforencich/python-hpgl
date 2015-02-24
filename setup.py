
from __future__ import with_statement

# http://docs.python.org/distutils/
# http://packages.python.org/distribute/
try:
    from setuptools import setup
except:
    from distutils.core import setup

import os.path

version_py = os.path.join(os.path.dirname(__file__), 'hpgl', 'version.py')
with open(version_py, 'r') as f:
    d = dict()
    exec(f.read(), d)
    version = d['__version__']

setup(
    name = 'python-hpgl',
    description = 'HPGL parsing library',
    version = version,
    long_description = '''This Python package supports parsing HP graphics language
for emulating HP printers and plotters.''',
    author = 'Alex Forencich',
    author_email = 'alex@alexforencich.com',
    url = 'http://alexforencich.com/wiki/en/python-hpgl/start',
    download_url = 'http://github.com/alexforencich/python-hpgl/tarball/master',
    keywords = 'HPGL',
    license = 'MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
        ],
    packages = ['hpgl'],
    entry_points = {
        'console_scripts': [
            'hpgl2svg = hpgl.cli:hpgl2svg',
            'hprtl2bmp = hpgl.cli:hprtl2bmp',
        ],
    },
)
