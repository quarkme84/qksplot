rootplots
=========

A python package to plot histograms, profile histograms using an interface similar to ROOT's plotting.

This package was inspired by ROOT Project’s histogramming library but it has no connection to ROOT and such it doesn’t
require ROOT, PyROOT, nor ROOTPy. Its also NOT compatible with ROOT’s libraries.

This package is structured in 3 modules:
    - a module for histograms: hist
    - another for profile histograms: prof
    - another for plotting: mpl

The modules **hist** and **prof** do not depend on any graphic/plotting library, even on mpl module. So, histograms and
profiles can be created and use all functionality without any dependency of graphics. But, mpl module is here for your
convenience to quickly make a plot.


Requirements
------------
python 3.3+ with **numpy**. And if you require easy plotting of rootplots.mpl you need also **matplotlib**


A simple Histogram example
--------------------------
Create a 1D histogram:

.. code:: python

   import random
   from rootplots import hist  # hist module contains histograms
   from rootplots import mpl  # mpl module helps to do plot

   # create a 1-Dimensional
   h1 = hist.Hist1D(100, -3, 3)  # histogram of 100 bins, first bin starts at -3.0, last bin ends at 3.0

   for x in range(100):
     # generate random numbers to fill the hist
     r = random.uniform(-1, 1)
     h1.fill(r)  # fill the histogram

   mpl.plot(h1)  # plot the histogram



A simple Profile
----------------

Filling a 1-D profile:

.. code:: python

    import random
    from rootplots.profile import Profile1D
    from rootplots import mpl

    # create profile
    prof = Profile1D(100, -4, 4)  # 100 bins, first bin starts at -4.0 and last bin is at 4.0

    # generate data...
    # and then fill the profile
    for x in range(2500):
        # generate random numbers to fill the hists
        px = random.gauss(0, 1)
        py = random.gauss(0, 1)

        pz = px * px + py * py

        prof.fill(px, value=pz)  # fill the profile

    prof.title = "Profile of pz versus px"

    # plot the profile
    mpl.plot(prof)
    mpl.show()

For more see  `the documentation  <https://quarkme84.github.io/rootplots/>`_.