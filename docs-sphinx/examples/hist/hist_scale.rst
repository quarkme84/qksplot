Scaling a histogram
===================

This example shows how to scale a histogram. To show the effect of the scalling, the initial histogram is copied in a different object before scaling, because the scalling modifies the original object.
Also, we use `matplotlib` to create a 2 by 2 grid to display multiple plots on the same window. The histograms are plotted using the plotting module `mpl` from this package (which internally uses matplotlib).

.. literalinclude:: hist_scale.py