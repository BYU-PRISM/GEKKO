# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))
# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

#APM binaries based on OS (currently only available for Windows)
#if os.name == 'nt':
#    apm_binary = {'gekko': ['bin/apm.exe']}
#else:
#    apm_binary = []
#elif linux:
#   apm_binary = ['gekko/bin/apmonitor' AND LA libaries]

setup(name='gekko',
    version='0.0.4a2',
    description='Optimization software for differential algebraic equations',
    long_description=long_description,
    #url="https://readthedocsurl",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='DAE optimization MILP MINLP QP NLP MIDO IPOPT',
    url='https://github.com/BYU-PRISM/GEKKO',
    author='BYU PRISM Lab',
    author_email='john_hedengren@byu.edu',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        #'APMonitor>=0.34',
        'numpy~=1.8'#,
        #'ujson',
    ],
#    package_data=apm_binary,
#   TODO add testing
#    test_suite='pytest.collector',
#    tests_require=['pytest'],
    python_requires='>=2.6',
    zip_safe=False)
