#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='measure-lookup-components',
    version='0.1',
    url='https://github.com/dmr/measure-lookup-components',
    license='MIT',
    author='Daniel Rech',
    author_email='danielmrech@gmail.com',
    description=(
        'Measures the components of requests to Smart Grid Actor servers. '
        'Requires url to query for Smart Grid Actor server addresses'
    ),
    py_modules= ['measure_lookup_components'],
    entry_points={
        'console_scripts': [
            'measure_lookup_components = measure_lookup_components:main',
        ],
    },
    install_requires=[
        'argparse',
        'pycurl',
        'pandas',
        'numpy',
        #statsmodels #optional
    ],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
