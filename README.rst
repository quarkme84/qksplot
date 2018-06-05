rootplots
=========

.. image:: http://img.shields.io/travis/Duke-QCD/hic.svg?style=flat-square
  :target: https://travis-ci.org/Duke-QCD/hic

Modules for N-dimensional histograms and profile plotting for data scientists - Inspired by ROOT project.

Installation
------------
Requirements: python 3.3+ with numpy_, random_.

Install the latest release with pip_::

   pip install rootplots

To run the tests, install nose_ and run ::

   nosetests -v hic

Simple examples
---------------
Create a 1D histogram:

.. code:: python

   import random
   from rootplots import hist

   h1 = hist.Hist1D(100, -3, 3)
   h1.fill(0.5)

Randomly sample events with specified flows:

.. code:: python

   sampler = flow.Sampler(v2, v3)
   phi = sampler.sample(mult)

Calculate initial condition eccentricities:

.. code:: python

   from hic import initial

   ic = initial.IC(profile, dxy)
   e2 = ic.ecc(2)

.. _numpy: http://www.numpy.org
.. _pip: https://pip.pypa.io
.. _nose: https://nose.readthedocs.org
