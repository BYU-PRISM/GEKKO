# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))
# Get the long description from the README file
#with open(os.path.join(here, 'description.rst'), encoding='utf-8') as f:
#    long_description = f.read()
long_description = """GEKKO
=====

GEKKO is a python package for machine learning and optimization, specializing in
dynamic optimization of differential algebraic equations (DAE) systems. GEKKO 
provides a user-friendly interface to the powerful APMonitor optimization suite
on the back end. It is coupled with large-scale solvers for linear, quadratic,
nonlinear, and mixed integer programming (LP, QP, NLP, MILP, MINLP). Capabilities
include machine learning, discrete or continuous models, real-time optimization, 
simulation, moving horizon estimation, and nonlinear predictive control."""

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

#gather all files for GUI support
gui_files = package_files('gekko/static')
#add APM executable file
extra_files = gui_files + ['bin/apm.exe','bin/apm','bin/apm_arm','bin/apm_mac']

#APM binaries based on OS (currently only available for Windows)
#if os.name == 'nt':
#    apm_binary = {'gekko': ['bin/apm.exe']}
#else:
#    apm_binary = []
#elif linux:
#   apm_binary = ['gekko/bin/apmonitor' AND LA libaries]

# versions: a (alpha), b (beta), rc (release candidate)
setup(name='gekko',
    version='0.2.1',
    description='Machine learning and optimization for dynamic systems',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='differential deep learning reinforcement optimization mixed-integer',
    url='https://github.com/BYU-PRISM/GEKKO',
    author='BYU PRISM Lab',
    author_email='john_hedengren@byu.edu',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        # 'APMonitor>=0.33',
        'flask',
        'flask_cors',
        'numpy>=1.8'#,
        #'ujson',
    ],
#    include_package_data=True,
#    package_dir={'':'gekko'},
    package_data={'gekko': extra_files},#['bin/apm.exe','static/*']},
#   TODO add testing
#    test_suite='pytest.collector',
#    tests_require=['pytest'],
    python_requires='>=2.6',
    zip_safe=False)
