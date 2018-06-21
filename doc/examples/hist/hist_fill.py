import random

from rootplots.hist import Hist1D
from rootplots import mpl

# create profile
h = Hist1D(100, -4, 4)

# generate data...
# and then fill the profile
for x in range(25000):
    # generate random numbers to fill the hists
    px = random.gauss(0, 1)

    h.fill(px)  # fill the profile

h.title = "Histogram"

# plot the profile
mpl.plot_hist(h)
mpl.show()
