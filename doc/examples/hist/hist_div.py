import random
import matplotlib.pyplot as plt

from rootplots.hist import Hist1D
from rootplots import mpl

# create histograms
h1 = Hist1D(10, -1, 1, title="H1")
h2 = Hist1D(10, -1, 1, title="H2")

# fill the histogram
for x in range(100):
	# generate random numbers to fill the hists
	r1 = random.uniform(-1,1)
	r2 = random.uniform(-1,1)

	h1.fill(r1)
	h2.fill(r2)

# divide the histograms, store the result in a third hist
h3 = h1 / h2
h3.title = "H1 / H2"

# create a grid where to rest the plots
grid = plt.GridSpec(2, 2, wspace=0.2, hspace=0.4)

# plot h1
plt.subplot(grid[0, 0])
mpl.plot_hist(h1)

# plot h2
plt.subplot(grid[0, 1])
mpl.plot_hist(h2)

# plot h3
plt.subplot(grid[1,0:])
mpl.plot_hist(h3)

mpl.show()
