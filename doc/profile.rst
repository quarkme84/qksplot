****************************
The Profile Histogram Module
****************************

This module contains classes for profile histograms. 

While histograms show the value filled in each their bin, profile histograms show the mean of the values and its root mean square filled in each bin.


The Profile Histogram Classes
=============================

This package provides full support for N-Dimensional profile histograms: :py:class:`ProfileND <rootplots.profile.ProfileND>` a class is derived from :py:class:`HistND <rootplots.Profile.ProfileND>`. 

But for your convenience, there are also classes derived from :py:class:`ProfileND <rootplots.profile.ProfileND>` 
that are more convenient to use when you need lower dimensional profile histograms:

	* :py:class:`Profile1D <rootplots.profile.Profile1D>` for 1D profile histograms
	* :py:class:`Profile2D <rootplots.profile.Profile2D>` for 2D profile histograms
	* :py:class:`Profile3D <rootplots.profile.Profile3D>` for 3D profile histograms


Creating Profile Histograms
===========================


importing the library
---------------------

But first we must import the profile histogram module::

	from rootplots.profile import *

This command imports all classes defined in rootplots.profile module, which includes classes for 1D, 2D, 3D and ND profile histograms.

1D Profile
----------

The easiest profile histograms to create are **one dimensional** (:py:class:`Profile1D <rootplots.profile.Profile1D>`)::

	h = Profile1D(100, -3.0, 3.0)

Above we created a 1D profile that contains *100 bins* starting from *-3.0* to *3.0*.

2D Profile
----------

To create **two dimensional** profiles (:py:class:`Profile2D <rootplots.profile.Profile2D>`) it gets a bit complex, because we must explicitly say how the bins are distributed on 2 axis.::

	h2 = Profile2D(100, -3, 3, 60, 0, 1000)


Here, we recongnize the first 3 arguments as representing the bin distribution on the first axis/dimension as we did previously for 1D case . For the second axis, we can see that it has 60 bins starting from 0 and grow equally spaced till 1000.

3D Profile
----------

A bit more complex is to create **three dimensional** profiles (:py:class:`Profile3D <rootplots.profile.Profile3D>`)::

	h3 = Profile3D(100, -3, 3, 60, 0, 1000, 80, -5, 3)


To construct 3D profiles, we basically do the same as for 2D histograms with the added difference we need 3 more arguments to specify bin distribution on the third axis. Pretty simple!

ND Profiles
-----------
When we want to go to **higher dimensions** then 3 we must use the **N-Dimensional profile class** (:py:class:`ProfileND <rootplots.profile.ProfileND>`). Here, the interface is a bit different since we must deal 
with **N** values for each parameter from the bin distribution. For this reason we must use *arrays* or *lists*::

	hN = ProfileND( N, minBins, maxBins, nBins)

Where *N* is the number of dimensions and the other arguments are arrays/lists. Where we understand that the *ith* element represents its value on *ith* dimension/axis. For example, a **5 dimensional histogram**::

	N=5
	mins = [0,0,0,0,0]
	maxis = [5,6,8,8,8]
	nbins = [5,6,8,10,10]

	h5 = ProfileND(N, mins, maxis, nbins)

or, simply::

	h5 = ProfileND(5, [0,-1,0,2,1], [5,6,8,8,11], [5,6,8,10,10])

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

	h2 = Profile2D(100, -3, 3, 60, 0, 1000, title="Nch vs Pt")


Filling
=======

A profile is useless if it is not filled. 

In this section we present the filling methods of profile of different dimensions. 
First, we start with the simples methods. We kept the more advanced functionality in a subsection of it own at the end of this section.

1D Profile
------------

One can fill a 1-dimensional Profile by simply calling the :py:meth:`fill <rootplots.profile.Profile1D.fill>` method::

	h.fill(x, value=val)

This methods automatically searches the bin at the position x and fills it with the value *val*. The number of entries in that bin is increased by 1.

You can specify a weight::

	h.fill(x, value=val, weight=w)

Which automatically searches the bin at the position x and fills it with the value *val*. The number of entries in that bin is increased by the weight *w*.

.. note::
	Using the fill methods there is no need to say which bin index you want filled, just a position that is inside a bin.

2D Profile
----------

The 2D Profile are filled similarly to 1D case, with the exception this time we must take care of 2 axis::

	h2.fill(X, Y, value=val)

Now, the :py:meth:`fill <rootplots.profile.Profile2D.fill>` method automatically searches the bin on the first axis that can contains the position *X* and the bin on the second axis that can contains the position *Y*, fills it with **val** and increases the entries in the bin by 1. 

.. note::
	You may wonder: since there are bins on X-axis and bins on Y-axis which bin its actually filled?

	The answear: None of those. Because those bins don't exists for the reason that internally, the profile classes contain **N-dimensional cells** also known as **global linear bins** as you may find it in other parts of the documentation. These cells represent the intersection of the bins from all axis.

Respectively, there is an argument for which you can specify a weight::

	h2.fill_w(X, Y, value=val, weight=w)

3D Profile
----------

Its obvious by now, the fill methods for the 3D profile are::

	h3.fill(X, Y, Z, value=val)

	# with a weight:
	h3.fill_w(X, Y, Z, value=val, weight=w)

ND Profile
----------

When going above 3 dimensions one must use an N values to specify a position. We must use a Sequence (arrays/lists) as arguments to the fill methods::

	p = [3.46, -0.33, 7.1, 2.28, 9]
	val = 0.33
	h5.fill(arr=p, value=val)

	# with weights
	h5.fill(arr=[3.46, -0.33, 7.1, 2.28, 9], value=0.33, weight=1.5)




Advanced Filling Methods
------------------------
There are more ways to fill.

Use :py:meth:`fill_pos <rootplots.profile.ProfileND.fill_pos>` when you know the a position on each axis::

	p = [1,0,100,2,86,47]
	v = 56.4
	hist.fill_pos(p, value=v)

	# with weight:
	w = 34.2
	hist.fill_pos(p, value=v, weight=w)

The methods :py:meth:`fill_pos <rootplots.profile.ProfileND.fill_pos>` is actually the same as the method :py:meth:`fill <rootplots.profile.ProfileND.fill>`, except it accepts only 2 arguments.

Use :py:meth:`fill_bins <rootplots.profile.ProfileND.fill_bins>` when you know the bins ids on each axis::

	mbins = [1,0,100,2,86,47]
	v = 56.4
	hist.fill_bins(mbins, value=v)

	# with weight:
	w = 34.2
	hist.fill_bins(mbins, value=v, weight=w)

.. note::
	The argument is a list of bin indexes. The dimension of the list must be the same as the dimension of the Profile.
	The bin indexes start from 0 to MaxBinIndex-1. MaxBinIndex is known when creating the Profile.

Use :py:meth:`fill_cell <rootplots.profile.ProfileND.fill_cell>` when you know the cell index::

	icell = 34
	v = 56.4
	hist.fill_bins(icell, value=v)

	# with weight:
	w = 2.2
	hist.fill_cell_w(icell, value=v, weight=w)

.. note::
	The cell index starts from 0 to MAX_CELL_IDX, where MAX_CELL_IDX is the product of all the bin counters from all dimensions.
	Meaning for a 5D Profile that contains `nbins=[5,6,8,10,10]` the `MAX_CELL_IDX=5*6*8*10*10`


Operations
==========

The histograms in this package support multiple operations done on them, such as Scaling, Adding, Substracting, Multiplying and Dividing between histograms.

Scaling
-------
Any histogram, whether its 1D, 2D, 3D or ND, can be scaled by a factor using the :py:meth:`scale <rootplots.profile.ProfileND.scale>` method.
Take the following example::

	# create a 1D histogram
	myhist = Hist1D(10, 0, 10)

	# fill the histogram
	for x in range(100):
		r = random.uniform(0,10)

		myhist.fill(r)

	# scale the histogram's bins by 2.3
	myhist.scale(2.3)

.. image:: examples/hist/images/h1_scalling.png

This method multiplies the internal bins (cells) by the value specified in the argument. The effect is visible in the above image where the vertical axis presents different values. Check a full example :doc:`examples/hist/hist_scale`


Adding histograms
-----------------

Histograms can be added by simply using the `+` operator::

	# add 2 histograms
	hSum = h1 + h2

.. figure:: examples/hist/images/h1D_add.png
	:alt: graphical representation of adding two 1D-histograms

	The plot of adding 2 histograms (top) and showing the resulted histogram (below). The plot was generated by the full example from :doc:`examples/hist/hist_add`


Substracting
------------

Histograms can be substracted by simply using the `-` operator::

	# substruct 2 histograms
	hDiff = h1 - h2

.. figure:: examples/hist/images/h1D_diff.png
	:alt: graphical representation of substracting two 1D-histograms

	The plot of substracting a histogram from another (top) and showing the resulted histogram (below). The plot was generated by the full example from :doc:`examples/hist/hist_diff`


Multiplying
-----------

Histograms can be multiplied by simply using the `*` operator::

	# multiply 2 histograms
	hDiff = h1 * h2

.. figure:: examples/hist/images/h1D_mult.png
	:alt: graphical representation of multiplication of two 1D-histograms

	The plot of multiplying two histogram from another (top) and showing the resulted histogram (below). The plot was generated by the full example from :doc:`examples/hist/hist_mult`


Dividing
--------

Histograms can be divided by simply using the `/` operator::

	# divide 2 histograms
	hDiff = h1 / h2

.. figure:: examples/hist/images/h1D_div.png
	:alt: graphical representation of dividing two 1D-histograms

	The plot of dividing two histogram from another (top) and showing the resulted histogram (below). The plot was generated by the full example from :doc:`examples/hist/hist_div`


Integrating
-----------

You can integrate the histogram (do the sum of the values of its internal cells multiplied with the volume described by its bins). 

To do the integration you have 3 ways or methods, they differ by the meaning of their arguments.

Use :py:meth:`integral_over_pos <rootplots.profile.ProfileND.integral_over_pos>` to do the integration over 2 position::

	p = [0.33, 4.61, 78.29, 11.2]
	q = [1.22, 3.2, 88, 27.0]
	h.integral_over_pos(p, q)

here *h* can be any dimensional histogram. The arguments *p* and *q* are two positions (arrays) and p < q.

Use :py:meth:`integral_over_bins <rootplots.profile.ProfileND.integral_over_bins>` when you know the bins::

	b1 = [0, 4, 5]
	b2 = [1, 1, 0]
	h.integral_over_bins(b1, b2)

here *h* can be any dimensional histogram. The arguments *b1* and *b2* are bins positions (arrays) and b1 < b2.

Use :py:meth:`integral <rootplots.profile.ProfileND.integral>` when you know the two cell indexes::

	c1 = 34
	c2 = 90
	h.integral_over_bins(c1, c2)

here *h* can be any dimensional histogram. The arguments *c1* and *c2* are cell indexes (integers) and c1 < c2.


Projections
===========

You can project any higher dimensional histogram to any lower dimensional histogram. The projection is also a histogram, containing less dimensions.


Projecting 2D histograms
------------------------

Projecting 2D histograms is easy::

	hproj = h2D.projectionX()

This projects a 2D histogram to its first axe (named X). The result *hproj* is a 1D histogram.

You can also project it on the second axe, called Y::

	hproj = h2D.projectionY()

.. figure:: examples/hist/images/h2D_proj.png
	:alt: projections of 2D histograms

	The 2D histogram above is projected along axes X and Y. See the full example :doc:`examples/hist/hist_proj`

Projecting 3D histograms
------------------------

Besides the usual projecting methods as seen for 2D histograms (:py:meth:`projectionX <rootplots.profile.Profile3D.projectionX>`, :py:meth:`projectionY <rootplots.profile.Profile3D.projectionY>`) we get specific methods for 3D such as :py:meth:`projectionZ <rootplots.profile.Profile3D.projectionZ>`. Also, we can make projections on multiple planes defined by different combinations of axis.

Thus, we get a projection on XY plane::

	hXYproj = h3D.projectionXY()

Or a projection on XZ plane::

	hXZproj = h3D.projectionXZ()

Or a projection on YZ plane::

	hYZproj = h3D.projectionYZ()


Projecting ND histograms
------------------------

We've seen how easy is to do projections for lower dimensional histograms.

When projecting higher dimensional histograms (HistND) we must be more explicit and specify which dimensions we keep while projecting. For example, when we used :py:meth:`projectionX <rootplots.profile.Profile3D.projectionX>` to project a 2D or 3D histogram on the X axis, the projection operation does this: **keep X axis** and all the rest axis are projected. When we used :py:meth:`projectionYZ <rootplots.profile.Profile3D.projectionYZ>` the projection operation **keeps Y & Z axis** and projects the rest (only X axis in this case). 

We must recognize a general projection algorithm can not contain the letters for N-dimensional histograms, we do not have that many letters. For this reason, we must specify an **array of axis indexes** the ones we want to keep. The first axis (called X) has index 0, Y is 1 and Z is 2.

Lets see some examples on how to project a 7 dimensional histogram::
	
	# create a 7 dimensional histogram
	h = HistND(7, [-1,0,0,0,0,0,0], [1,10,10,10,10,10,10], [10,10,10,10,10,10,10])

	# code to fill the histogram
	# ...
	# ...
	# ...

	# create a projection on the first axis (aka X)
	hXproj = h.projection([0])

	# create a projection on the second axis (aka Y)
	hYproj = h.projection([1])

	# create a projection on the 7th axis
	hproj = h.projection([6])

	# create a projection on XY
	hXYproj = h.projection([0,1])

	# create a projection on X and the 5th axis
	hX5proj = h.projection([0,4])

	# create a projection on XYZ
	hXYZproj = h.projection([0,1,2])

	# create a projection on XYZ and the 5th & 7th axis
	hproj = h.projection([0,1,2,4,6])


Drawing
=======

The Histogramming module's design is intended only for histogramming in order to let the user decide which library they prefer for plotting. Hence, this module has no drawing/plotting capabilities.

We recognized the need to plot easy and quickly and for this reason the rootplots package provides a separate module specifically created to quickly draw the histograms objects. Go read about it here.


Reference Documentation
=======================

.. toctree::
   :includehidden:
   :maxdepth: 2

   examples/profile/index
   reference_profile