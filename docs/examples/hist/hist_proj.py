import random as rnd
import matplotlib.pyplot as plt

from rootplots.hist import *
from rootplots import mpl

# create histograms
h = Hist2D(30, -5, 5, 30, 0, 10, title="H2")

# fill the histogram
x, y = 0, 0
for i in range(50000):
    x = rnd.gauss(0, 2)
    y = 10 - rnd.expovariate(1./4.)
    h.fill(x, y)

projX = h.projection_x()
projX.title = "Projection on X"

projY = h.projection_y()
projY.title = "Projection on Y"

# create a grid where to rest the plots
grid = plt.GridSpec(3, 1, wspace=0.2, hspace=0.4)

# plot h
plt.subplot(grid[0, 0])
mpl.plot_hist(h)

# plot projection on X
plt.subplot(grid[1, 0])
mpl.plot_hist(projX)

# plot projection on Y
plt.subplot(grid[2, 0])
mpl.plot_hist(projY)

mpl.show()
