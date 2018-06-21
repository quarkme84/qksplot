import random
import copy
import matplotlib.pyplot as plt

from rootplots.hist import Hist1D
from rootplots import mpl

# create a 1D histogram
myhist = Hist1D(10, 0, 10)

# fill the histogram
for x in range(100):
    r = random.uniform(0, 10)

    myhist.fill(r)

# make a copy before scalling
histBeforeScaling = copy.deepcopy(myhist)
histBeforeScaling.title = "Before Scaling"

# scale the histogram's bins by 2.3
histAfterScaling = myhist.scale(2.3)
histAfterScaling.title = "After Scaling"

grid = plt.GridSpec(1, 2, wspace=0.2, hspace=0.4)
plt.subplot(grid[0, 0])
mpl.plot_hist(histBeforeScaling)

plt.subplot(grid[0, 1])
mpl.plot_hist(histAfterScaling)

mpl.show()
