# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))
long_description = """GEKKO
=====

GEKKO is a python package for machine learning and optimization, specializing in
dynamic optimization of differential algebraic equations (DAE) systems. It is coupled 
with large-scale solvers APOPT and IPOPT for linear, quadratic, nonlinear, and mixed integer 
programming. Capabilities include machine learning, discrete or continuous state space
models, simulation, estimation, and control.

Gekko models consist of equations and variables that create a symbolic representation of the
problem for a single data point or single time instance. Solution modes then create the full model
over all data points or time horizon. Gekko supports a wide range of problem types, including:

- Linear Programming (LP)
- Quadratic Programming (QP)
- Nonlinear Programming (NLP)
- Mixed-Integer Linear Programming (MILP)
- Mixed-Integer Quadratic Programming (MIQP)
- Mixed-Integer Nonlinear Programming (MINLP)
- Differential Algebraic Equations (DAEs)
- Mathematical Programming with Complementarity Constraints (MPCCs)
- Data regression / Machine learning
- Moving Horizon Estimation (MHE)
- Model Predictive Control (MPC)
- Real-Time Optimization (RTO)
- Sequential or Simultaneous DAE solution

Gekko compiles the model into byte-code and provides sparse derivatives to the solver with
automatic differentiation. Gekko includes data cleansing functions and standard tag actions for industrially 
hardened control and optimization on Windows, Linux, MacOS, ARM processors, or any other platform that 
runs Python. Options are available for local, edge, and cloud solutions to manage memory or compute 
resources.

- [Gekko Homepage](https://machinelearning.byu.edu)
- [Gekko Documentation](https://gekko.readthedocs.io/en/latest/)
- [Gekko Examples](https://apmonitor.com/wiki/index.php/Main/GekkoPythonOptimization)
- [Get Gekko Help on Stack Overflow](https://stackoverflow.com/questions/tagged/gekko)

"""

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

#gather all files for GUI support
gui_files = package_files('gekko/static')
#add APM executable file
extra_files = gui_files + ['bin/apm.exe','bin/apm','bin/apm_aarch64','bin/apm_arm','bin/apm_mac']

# versions: a (alpha), b (beta), rc (release candidate)
# update version here, __init__.py, and create a GitHub release
setup(name='gekko',
    version='1.2.1',
    description='Machine learning and optimization for dynamic systems',
    long_description=long_description,
    long_description_content_type = 'text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='differential deep learning solver equations optimization mixed-integer',
    url='https://github.com/BYU-PRISM/GEKKO',
    author='BYU PRISM Lab',
    author_email='support@apmonitor.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        #'flask',
        #'flask_cors',
        'numpy>=1.8'#,
        #'ujson',
    ],
    package_data={'gekko': extra_files},
    python_requires='>=2.6',
    zip_safe=False)
