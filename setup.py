# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()


setup(name='gekko',
    version='0.0.1rc1',
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
    #url='https://github.com',
    author='BYU PRISM Lab',
    author_email='john_hedengren@byu.edu',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'APMonitor',
        'numpy'#,
        #'ujson',
    ],
#    scripts=[
#        'gekko/bin/apmonitor',
#        'gekko/bin/apm.exe'
#    ],
#   TODO add testing
#    test_suite='pytest.collector',
#    tests_require=['pytest'],
    python_requires='>=2.6',
    zip_safe=False)




