from rootplots.hist import HistND
import matplotlib.pyplot as plt
import random as rnd


def plot_h1(h):
    xbins = h.get_bins_edges()
    x = h.get_bins_centers()
    w = h.get_cells_contents()

    plt.xlabel(h.get_axis(0).title)
    plt.title(h.title)
    plt.hist(x[0], bins=xbins[0], weights=w)
    plt.show()


def plot_h2(h):
    axis_bins = h.get_bins_edges(True)
    centers = h.get_bins_centers()
    w = h.get_cells_contents()

    plt.figure()
    plt.xlabel(h.get_axis(0).title)
    plt.ylabel(h.get_axis(1).title)
    plt.title(h.title)
    plt.hist2d(centers[0], centers[1], bins=axis_bins, weights=w)
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')
    plt.show()


def test_plotting(h: HistND):
    print("-"*50)
    print("Testing histogram: ", h.title)
    print("stats: ", h.get_stats())

    if h.dimension == 1:
        plot_h1(h)
    elif h.dimension == 2:
        plot_h2(h)
    else:
        print("unable to plot this dimension")


h1 = HistND(1,[40], [160], [100], title="H1")

h2 = HistND(2, [-5,0], [5,10], [30,30], title="H2")
h2.get_axis(0).title = 'x'
h2.get_axis(1).title = 'y'

# h3 = HistND(3,[0,0,0], [5,6,8], [5,6,8], title="H3")

# x = 0
# for i in range(2500):
#     x = rnd.gauss(100,5)
#     h1.fill_bin([x])

x, y = 0, 0
for i in range(500000):
    x = rnd.gauss(0,2)
    y = 10 - rnd.expovariate(1./4.)
    h2.fill_pos_w([x, y], 1)

# test_plotting(h1)
test_plotting(h2)
# test_plotting(h3)

projX = h2.projection([0])
projX.title = "Projection on X"

projY = h2.projection([1])
projY.title = "Projection on Y"

projXY = h2.projection([0,1])
projXY.title = "Projection on XY"

test_plotting(projX)
test_plotting(projY)
test_plotting(projXY)

