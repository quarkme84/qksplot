import random

from qksplot.profile import Profile1D
from qksplot import mpl

# create profile
prof = Profile1D(100, -4, 4)

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
