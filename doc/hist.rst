************************
The Histogramming Module
************************

This module contains classes for histogramming. 

We'll cover the classes and their functionalities by directly using them in different examples.

The Histogram Classes
=====================

This package provides full support for N-Dimensional histograms: :py:class:`HistND <rootplots.hist.HistND>`.
But for your convenience, there are also classes derived from :py:class:`HistND <rootplots.hist.HistND>` 
that are more convenient to use when you need lower dimensional histograms:

	* :py:class:`Hist1D <rootplots.hist.Hist1D>` a 1D histogram
	* :py:class:`Hist2D <rootplots.hist.Hist2D>` a 2D histogram
	* :py:class:`Hist3D <rootplots.hist.Hist3D>` a 3D histogram


Regardles of the histogram's dimension, the bins are all *floats* and *equal width* on the axis. As such, for the moment the histograms don't support
non-linear axis such as logarithmic axis.

Creating Histograms
===================

To create a histogram we must say how the bins are distributed on each axis (per dimension). 
For each dimension of the histogram, the expected information is: the number of bins per axis,
the minimum value on the axis of the lowest bin and the maximum value on the axis of the highest bin.

importing the library
---------------------

But first we must import the histogram module::

	from rootplots.hist import *

This command imports all classes defined in rootplots.hist module, more precisly the classes for 1D, 2D, 3D and ND histograms.

1D histogram
------------

The easiest histograms to create are **one dimensional** (:py:class:`Hist1D <rootplots.hist.Hist1D>`)::

	h = Hist1D(100, -3.0, 3.0)

Above we created a 1D histogram that contains *100 bins* starting from *-3.0* to *3.0*.

2D histogram
------------

To create **two dimensional** histograms (:py:class:`Hist2D <rootplots.hist.Hist2D>`) it gets a bit complex, because we must explicitly say how the bins are distributed on 2 axis.::

	h2 = Hist2D(100, -3, 3, 60, 0, 1000)


Here, we recongnize the first 3 arguments as representing the bin distribution on the first axis/dimension as we did previously for *h* . For the second axis, we can see that it has 60 bins starting from 0 and grow equally spaced till 1000.

3D histogram
------------

A bit more complex is to create **three dimensional** histograms (:py:class:`Hist3D <rootplots.hist.Hist3D>`)::

	h3 = Hist3D(100, -3, 3, 60, 0, 1000, 80, -5, 3)


To construct 3D histograms is basically the same as for 2D histograms with the added difference we need 3 more arguments to specify bin distribution on the third axis. Pretty simple!

ND histogram
------------
When we want to go to **higher dimensions** then 3 we must use the **N-Dimensional histogram class** (:py:class:`HistND <rootplots.hist.HistND>`). Here, the interface is a bit different since we must deal 
with **N** values for each parameter from the bin distribution. For this reason we must use *arrays* or *lists*::

	hN = HistND( N, minBins, maxBins, nBins)

Where *N* is the number of dimensions and the other arguments are arrays/lists. Where we understand that the *ith* element represents its value on *ith* dimension/axis. For example, a **5 dimensional histogram**::

	N=5
	mins = [0,0,0,0,0]
	maxis = [5,6,8,8,8]
	nbins = [5,6,8,10,10]

	h5 = HistND(N, mins, maxis, nbins)

or, simply::

	h5 = HistND(5, [0,-1,0,2,1], [5,6,8,8,11], [5,6,8,10,10])

We interpret as:

	- the histogram has 5 dimensions
	- the first axis has 5 bins starting from 0 till 5
	- the second axis has 6 bins starting from -1 till 6
	- the third axis has 8 bins starting from 0 till 8
	- the fourth axis has 10 bins starting from 2 till 8
	- the fifth axis has 10 bins starting from 1 till 11

.. warning::
	N-dimensional histogramming is very demanding of memory: a HistND with 8 dimensions and 100 bins per dimension needs more than 2.5GB of RAM!

the title of the histogram
--------------------------

There is one more argument that all histogram classes share it. We didn't show it because its not important to the histogramming functionality, the argument is the *title* of the histogram. This argument is only used to keep it around untill the moment of drawing the histogram. That's his only functionality.

Let's see an example on how to use **title** it in the constructor::

	h2 = Hist2D(100, -3, 3, 60, 0, 1000, title="Nch vs Pt")


Filling
=======

A histogram is useless if it is not filled. 

In this section we present the filling methods of histograms of different dimensions. 
First, we start with the simples methods. We kept the more advanced functionality in a subsection of it own at the end of this section.

1D histogram
------------

One can fill a 1-dimensional histogram by simply calling the :py:meth:`fill <rootplots.hist.Hist1D.fill>` method::

	h.fill(val)

This methods automatically searches the bin that can contain the value *val* and adds 1 to the counter of the bin. 

You can specify a weight using the :py:meth:`fill_w <rootplots.hist.Hist1D.fill_w>` method::

	h.fill_w(val, w)

Which automatically searches the bin that can contain the value *val* and adds the weight *w* to the counter of the bin.

.. note::
	Using the simple fill methods there is no need to say which bin you want filled, just a position that is inside a bin.

2D histogram
------------

The 2D histograms are filled similary to 1D case, with the exception  this time we must take care of 2 axis::

	h2.fill(valX, valY)

Now, the :py:meth:`fill <rootplots.hist.Hist2D.fill>` method automatically searches the bin on the first axis (alternatively called X-axis) that can contain the value *valX* and the bin on the second axis (aka called Y-axis) that can contain the value *valY* and adds 1 to the counter of the bin. 

.. note::
	You may wonder: since there are bins on X-axis and bins on Y-axis which bin its actually filled?

	The answear: None of those. Because those bins don't exists for the reason that internally, the histogram classes contain **N-dimensional cells** also known as **global linear bins** as you may find it in other parts of the documentation. These cells represent the intersection of the bins from all axis.

Respectively, there is a :py:meth:`fill_w <rootplots.hist.Hist2D.fill_w>` method for which you can specify a weight::

	h2.fill_w(valX, valY, w)

3D histogram
------------

Its obvious by now, the fill methods for the 3D histogram are::

	h3.fill(valX, valY, valZ)

respectively::

	h3.fill_w(valX, valY, valZ, w)

ND histogram
------------

When going above 3 dimensions one must use an n-dimensional histogram: :py:class:`HistND <rootplots.hist.HistND>`.

By now, you should noticed that for the above examples we filled the histogram's cells using positions and the arguments are simple variables. When we go to the general case (n-dimensional histogram) this is not enough. We must use arrays/lists as arguments to the fill methods and explicitly specify the meaning of the argument. So, there is **no fill method for the ND histograms**, instead there is :py:meth:`fill_pos <rootplots.hist.HistND.fill_pos>` which has the same meaning::

	p = [3.46, -0.33, 7.1, 2.28, 9]
	h5.fill_pos(p)

or, :py:meth:`fill_pos_w <rootplots.hist.HistND.fill_pos_w>` fills with weights::

	h5.fill_pos_w([3.46, -0.33, 7.1, 2.28, 9], 8)

The fill_pos method fills the bins (or the cell) that can contain the point defined at position p.

.. note::
	fill_pos does the same thing as the fill method and is available to all histograms. The fundamental difference is that fill is available only to histograms lower then 3D. Another difference is that fill_pos accepts only an array-like variable.

Advanced Filling Methods
------------------------

Untill now, we have seen some methods that histograms can use for filling:

 	- 2 methods for that histograms lower then 3D (fill & fill_pos) 
 	- 1 method for histograms higher then 3D (fill_pos)

These methods fill the histogram according to a position of a point that falls inside a bin. But, there are more ways to fill.

Use :py:meth:`fill_bins <rootplots.hist.HistND.fill_bins>` when you know the bins ids on each axis::

	mbins = [1,0,100,2,86,47]
	hist.fill_bins(mbins)

and :py:meth:`fill_bins_w <rootplots.hist.HistND.fill_bins_w>` with weight::

	mbins = [1,0,100,2,86,47]
	w = 34.2
	hist.fill_bins_w(mbins, w)

.. note::
	The argument is a list of bin indexes. The dimension of the list must be the same as the dimension of the histogram.
	The bin indexes start from 0 to MaxBinIndex-1. MaxBinIndex is known when creating the histogram.

Use :py:meth:`fill_cell <rootplots.hist.HistND.fill_cell>` when you know the cell index::

	icell = 34
	hist.fill_bins(icell)

and :py:meth:`fill_cell_w <rootplots.hist.HistND.fill_cell_w>` with weight::

	icell = 34
	w = 2.2
	hist.fill_cell_w(icell, w)

.. note::
	The cell index starts from 0 to MAX_CELL_IDX, where MAX_CELL_IDX is the product of all the bin counters from all dimensions.
	Meaning for a 5D histogram that contains `nbins=[5,6,8,10,10]` the `MAX_CELL_IDX=5*6*8*10*10`


Operations
==========




Projections
===========


Drawing
=======



API Reference
=============

.. toctree::
   :includehidden:

   reference_hist