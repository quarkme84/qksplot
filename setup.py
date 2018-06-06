#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import rootplots

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='rootplots',
    version=rootplots.__version__,
    description='Helpful offline plotting modules for Scientists',
    long_description=long_description,
    author='Mihai Niculescu',
    author_email='mihai@spacescience.ro',
    url='',
    license='GPL',
    packages=['rootplots', 'rootplots.tests'],
    install_requires=['numpy','typing'],
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
