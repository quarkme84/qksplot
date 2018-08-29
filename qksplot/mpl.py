"""
This module contains functions to make it easy to plot objects (Histograms, Profiles) from qksplot package using the
popular matplotlib library

@author: Mihai Niculescu <mihai@spacescience.ro>
"""
import matplotlib.pyplot as plt

from . import hist as hist
from . import profile as prof


def show():
    """ Force showing the figure"""
    plt.show()


def plot_h1(h: hist.HistND):
    if h.dimension != 1:
        return
    xbins = h.get_bins_edges(True)
    x = h.get_bins_centers()
    w = h.get_cells_contents()

    plt.xlabel(h.get_axis(0).title)
    plt.title(h.title)
    plt.hist(x[0], bins=xbins[0], weights=w)


def plot_h2(h: hist.HistND):
    if h.dimension != 2:
        return
    axis_bins = h.get_bins_edges(True)
    centers = h.get_bins_centers()
    w = h.get_cells_contents()

    plt.xlabel(h.get_axis(0).title)
    plt.ylabel(h.get_axis(1).title)
    plt.title(h.title)
    plt.hist2d(centers[0], centers[1], bins=axis_bins, weights=w)
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')


def plot_hist(h: hist.HistND):
    """ Plot a Histogram"""
    if h.dimension == 1:
        plot_h1(h)
    elif h.dimension == 2:
        plot_h2(h)
    else:
        print("unable to plot beyond 2 dimensions")


def plot_prof1(p: hist.HistND):
    if p.dimension != 1:
        return

    x = p.get_bins_centers()
    y = p.get_cells_contents()
    err_x = p.get_axis(0).get_bin_width(0)
    err_y = p.get_cells_contents_errors()

    plt.figure()
    plt.xlabel(p.get_axis(0).title)
    plt.title(p.title)
    plt.errorbar(x[0], y, xerr=err_x, yerr=err_y, marker=',', linestyle='None')


def plot_prof2(p: hist.HistND):
    if p.dimension != 2:
        return


def plot_profile(p: prof.ProfileND):
    """ Plot a Profile"""
    if p.dimension == 1:
        plot_prof1(p)
    elif p.dimension == 2:
        plot_prof2(p)
    else:
        print("unable to plot beyond 2 dimensions")


def plot(p):
    """ Plot a Histogram or a Profile"""
    if type(p) is hist.HistND or type(p) is hist.Hist1D or type(p) is hist.Hist2D or type(p) is hist.Hist3D:
        plot_hist(p)
        return

    if type(p) is prof.ProfileND or type(p) is prof.Profile1D or type(p) is prof.Profile2D or type(p) is prof.Profile3D:
        plot_profile(p)
        return


