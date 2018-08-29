****************************
The Profile Histogram Module
****************************

This module contains classes for profile histograms. 

While histograms show the value filled in each their bin, profile histograms show the mean of the values and its root mean square filled in each bin.


The Profile Histogram Classes
=============================

This package provides full support for N-Dimensional profile histograms: :py:class:`ProfileND <qksplot.profile.ProfileND>` a class is derived from :py:class:`HistND <qksplot.Profile.ProfileND>`.

But for your convenience, there are also classes derived from :py:class:`ProfileND <qksplot.profile.ProfileND>`
that are more convenient to use when you need lower dimensional profile histograms:

	* :py:class:`Profile1D <qksplot.profile.Profile1D>` for 1D profile histograms
	* :py:class:`Profile2D <qksplot.profile.Profile2D>` for 2D profile histograms
	* :py:class:`Profile3D <qksplot.profile.Profile3D>` for 3D profile histograms


Creating Profile Histograms
===========================


importing the library
---------------------

But first we must import the profile histogram module::

	from qksplot.profile import *

This command imports all classes defined in qksplot.profile module, which includes classes for 1D, 2D, 3D and ND profile histograms.

1D Profile
----------

The easiest profile histograms to create are **one dimensional** (:py:class:`Profile1D <qksplot.profile.Profile1D>`)::

	prof = Profile1D(100, -3.0, 3.0)

Above we created a 1D profile that contains *100 bins* starting from *-3.0* to *3.0*.

2D Profile
----------

To create **two dimensional** profiles (:py:class:`Profile2D <qksplot.profile.Profile2D>`) it gets a bit complex, because we must explicitly say how the bins are distributed on 2 axis.::

	prof2 = Profile2D(100, -3, 3, 60, 0, 1000)


Here, we recongnize the first 3 arguments as representing the bin distribution on the first axis/dimension as we did previously for 1D case . For the second axis, we can see that it has 60 bins starting from 0 and grow equally spaced till 1000.

3D Profile
----------

A bit more complex is to create **three dimensional** profiles (:py:class:`Profile3D <qksplot.profile.Profile3D>`)::

	prof = Profile3D(100, -3, 3, 60, 0, 1000, 80, -5, 3)


To construct 3D profiles, we basically do the same as for 2D histograms with the added difference we need 3 more arguments to specify bin distribution on the third axis. Pretty simple!

ND Profiles
-----------
When we want to go to **higher dimensions** then 3 we must use the **N-Dimensional profile class** (:py:class:`ProfileND <qksplot.profile.ProfileND>`). Here, the interface is a bit different since we must deal
with **N** values for each parameter from the bin distribution. For this reason we must use *arrays* or *lists*::

	profN = ProfileND( N, minBins, maxBins, nBins)

Where *N* is the number of dimensions and the other arguments are arrays/lists. Where we understand that the *ith* element represents its value on *ith* dimension/axis. For example, a **5 dimensional histogram**::

	N=5
	mins = [0,0,0,0,0]
	maxis = [5,6,8,8,8]
	nbins = [5,6,8,10,10]

	prof5 = ProfileND(N, mins, maxis, nbins)

or, simply::

	prof5 = ProfileND(5, [0,-1,0,2,1], [5,6,8,8,11], [5,6,8,10,10])

We interpret as:

	- the profile has 5 dimensions
	- the first axis has 5 bins starting from 0 till 5
	- the second axis has 6 bins starting from -1 till 6
	- the third axis has 8 bins starting from 0 till 8
	- the fourth axis has 10 bins starting from 2 till 8
	- the fifth axis has 10 bins starting from 1 till 11

.. warning::
	N-dimensional profile histograms are very demanding of memory: a ProfileND with 8 dimensions and 100 bins per dimension needs more than 2.5GB of RAM!

the title of the Profile
------------------------

There is one more argument that all profile classes share it. We didn't show it because its not important to the histogramming functionality, the argument is the *title* of the profile. This argument is only used to keep it around untill the moment of drawing the profile. That's his only functionality.

Let's see an example on how to use **title** it in the constructor::

	prof = Profile2D(100, -3, 3, 60, 0, 1000, title="Nch vs Pt")


Filling
=======

A profile is useless if it is not filled. 

In this section we present the filling methods of profile of different dimensions. 
First, we start with the simples methods. We kept the more advanced functionality in a subsection of it own at the end of this section.

1D Profile
------------

One can fill a 1-dimensional Profile by simply calling the :py:meth:`fill <qksplot.profile.Profile1D.fill>` method::

	prof.fill(x, value=val)

This methods automatically searches the bin at the position x and fills it with the value *val*. The number of entries in that bin is increased by 1.

You can specify a weight::

	prof.fill(x, value=val, weight=w)

Which automatically searches the bin at the position x and fills it with the value *val*. The number of entries in that bin is increased by the weight *w*.

.. note::
	Using the fill methods there is no need to say which bin index you want filled, just a position that is inside a bin.

2D Profile
----------

The 2D Profile are filled similarly to 1D case, with the exception this time we must take care of 2 axis::

	prof2.fill(X, Y, value=val)

Now, the :py:meth:`fill <qksplot.profile.Profile2D.fill>` method automatically searches the bin on the first axis that can contains the position *X* and the bin on the second axis that can contains the position *Y*, fills it with **val** and increases the entries in the bin by 1.

.. note::
	You may wonder: since there are bins on X-axis and bins on Y-axis which bin its actually filled?

	The answear: None of those. Because those bins don't exists for the reason that internally, the profile classes contain **N-dimensional cells** also known as **global linear bins** as you may find it in other parts of the documentation. These cells represent the intersection of the bins from all axis.

Respectively, there is an argument for which you can specify a weight::

	prof2.fill(X, Y, value=val, weight=w)

3D Profile
----------

Its obvious by now, the fill methods for the 3D profile are::

	prof3.fill(X, Y, Z, value=val)

	# with a weight:
	prof3.fill(X, Y, Z, value=val, weight=w)

ND Profile
----------

When going above 3 dimensions one must use an N values to specify a position. We must use a Sequence (arrays/lists) as arguments to the fill methods::

	p = [3.46, -0.33, 7.1, 2.28, 9]
	val = 0.33
	prof5.fill(*p, value=val)

	# with weights
	prof5.fill(3.46, -0.33, 7.1, 2.28, 9, value=0.33, weight=1.5)



Advanced Filling Methods
------------------------
There are more ways to fill.

Use :py:meth:`fill_pos <qksplot.profile.ProfileND.fill_pos>` when you know the a position on each axis::

	p = [1,0,100,2,86,47]
	v = 56.4
	prof.fill_pos(*p, value=v)

	# with weight:
	w = 34.2
	prof.fill_pos(*p, value=v, weight=w)

Use :py:meth:`fill_bins <qksplot.profile.ProfileND.fill_bins>` when you know the bins ids on each axis::

	mbins = [1,0,100,2,86,47]
	v = 56.4
	prof.fill_bins(*mbins, value=v)

	# with weight:
	w = 34.2
	prof.fill_bins(*mbins, value=v, weight=w)

.. note::
	The argument is a list of bin indexes. The dimension of the list must be the same as the dimension of the Profile.
	The bin indexes start from 0 to MaxBinIndex-1. MaxBinIndex is known when creating the Profile.

Use :py:meth:`fill_cell <qksplot.profile.ProfileND.fill_cell>` when you know the cell index::

	icell = 34
	v = 56.4
	prof.fill_bins(icell, value=v)

	# with weight:
	w = 2.2
	prof.fill_cell_w(icell, value=v, weight=w)

.. note::
	The cell index starts from 0 to MAX_CELL_IDX, where MAX_CELL_IDX is the product of all the bin counters from all dimensions.
	Meaning for a 5D Profile that contains `nbins=[5,6,8,10,10]` the `MAX_CELL_IDX=5*6*8*10*10`


Operations
==========

Since the profiles are derived from histograms they also support the same operations done on histograms: such as Scaling, Adding, Substracting, Multiplying, Dividing and Integrating. See the histograms documentation on how to apply these operations on profiles.


Projections
===========

Since the profiles are derived from histograms they also support the same projections as histograms. You can project any dimensional profile to any lower dimensional profile. The projection is a histogram containing less dimensions. See the histograms documentation on how to do projections.

Drawing
=======

The Profile module's design is intended only for profilling in order to let the user decide which library they prefer for plotting. Hence, this module has no drawing/plotting capabilities. But, we recognized the need to plot easy and quickly and for this reason the qksplot package provides a separate module specifically created to quickly draw profile objects. Go read about it here.


Reference Documentation
=======================

.. toctree::
   :includehidden:
   :maxdepth: 2

   examples/profile/index
   reference_profile