# -*- coding: utf-8 -*-

import random
import matplotlib.pyplot as plt

from rootplots.hist import Hist1D
from rootplots import mpl

# create histograms
h1 = Hist1D(10, -1, 1, title="Basic H1")
h2 = Hist1D(10, -1, 1, title="Basic H2")

for x in range(100):
	r = random.uniform(-1,1)
	#print("r=", r)

	h1.fill(r)
	h2.fill(random.uniform(-1,1))

h3 = h1 + h2

grid = plt.GridSpec(4, 2, wspace=0.2, hspace=0.4)
plt.subplot(grid[0, 0])
mpl.plot_hist(h1)

plt.subplot(grid[0, 1])
mpl.plot_hist(h2)

scaling_factor = 2.0
scaledHist = h1.scale(scaling_factor)

scaledHist.title = "H1 Scaled by " + str(scaling_factor)
plt.subplot(grid[1, 0])
mpl.plot_hist(scaledHist)


h3.title = "H1+H2"
plt.subplot(grid[1, 1])
mpl.plot_hist(h3)

print(h1.get_axis(0).__dict__)
print(h2.get_axis(0).__dict__)
print(h3.get_axis(0).__dict__)

print("-"*50)

print(h1.__dict__)
print(h2.__dict__)
print(h3.__dict__)
mpl.show()