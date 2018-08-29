#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import qksplot

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='qksplot',
    version=qksplot.__version__,
    description='Helpful offline plotting modules for Scientists',
    long_description=long_description,
    author='Mihai Niculescu',
    author_email='mihai@spacescience.ro',
    url='',
    license='GPL',
    packages=['qksplot', 'qksplot.tests'],
    install_requires=['numpy', 'typing', 'matplotlib'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GPL License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: Physics'
    ]
)
