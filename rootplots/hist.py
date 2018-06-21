# -*- coding: utf-8 -*-
"""
This module defines classes required for histogramming:
    :class:`Hist1D <Hist1D>` - A 1D histogram

    :class:`Hist2D <Hist2D>` - A 2D histogram

    :class:`Hist3D <Hist3D>` - A 3D histogram

    :class:`HistND <HistND>` - An N-Dimensional histogram

Note:
    The classes defined in this module do **NOT** provide drawing capabilities, so there is **NO** draw() nor paint()
    method. Use other libraries like matplotlib to plot the data. But for your convenience, this package provides a 
    module for easy plotting using matplotlib. See, :py:mod:`rootplots.mpl`

"""

import math
import warnings
import numpy as np
from typing import List, Dict, Sequence
from bisect import bisect_left

__all__ = 'HistAxis', 'HistND', 'Hist1D', 'Hist2D', 'Hist3D'


class HistAxis:
    """ An axis for use in constructing histograms

    Args:
        bins (Sequence): an ordered (ascending order) array of floats containing the lower edges of the bins

    """
    def __init__(self, bins, title=str()):
        self._label = title  # the label of the axis
        self._bins = bins  # an array with the low edges of the bins

    @property
    def minBin(self) -> float:
        """ returns the minimum low edge of first bin """
        return self._bins[0]

    @property
    def maxBin(self) -> float:
        """ returns the maximum right edge of the last bin """
        return self._bins[-1]

    @property
    def nbins(self) -> int:
        """ returns the total number of the bins"""
        return len(self._bins) - 1

    @property
    def title(self) -> str:
        return self._label

    @title.setter
    def title(self, label: str) -> None:
        """ sets the label of the axis"""
        self._label = label

    def density(self) -> float:
        """ the density of the bins = number of bins over the length (maxBin - minBin)"""
        if self.minBin != self.maxBin:
            return self.nbins / (self.maxBin - self.minBin)
        else:
            raise ValueError("MinBin can not be equalx to MaxBin.")

    def get_bin(self, x: float) -> int:
        """ Returns the bin index that contains 'x' value, such that for that bin ``minBin <= x < maxBin``

        Args:
            x (float): a valid value on the axis

        Returns:
            int. Or, -1 is returned if there is no such bin.
        """
        if x < self.minBin or x > self.maxBin:  # sane check
            return -1

        return bisect_left(self._bins, x) - 1

    def get_bins(self) -> Sequence:
        """ Returns all bins lower edges of the axis.

        Returns:
            List[float]. A list with lower edges of each bin
        """
        return self._bins

    def get_bin_center(self, i: int) -> float:
        """ Returns the value of the center in bin 'i' """
        return self._bins[i] + 0.5*self.get_bin_width(i)

    def get_bins_centers(self):
        """ Returns the a list containing the centers of all bins."""
        result = []
        for i, lowEdge in enumerate(self._bins):
            result.append(lowEdge+0.5*self.get_bin_width(i))
        return result

    def get_bin_lower_edge(self, i: int) -> float:
        return self._bins[i]

    def get_bin_upper_edge(self, i: int) -> float:
        return self._bins[i+1]

    def get_bin_width(self, i: int) -> float:
        if 0 <= i < self.nbins-1:
            return self._bins[i+1] - self._bins[i]
        elif i == self.nbins - 1:
            return self.get_bin_width(i-1)
        else:
            return 0.0


class HistND:
    """ An N-Dimensional Histogram.

        Args:
            dim (int): the number of dimensions of the histogram

            minBin (Sequence): an array containing the minimum value of lower (leftmost) edge of bins for each dimension.

            maxBin (Sequence): an array containing the maximum value of upper (rightmost) edge of bins for each dimension.

            nBins (Sequence):  an array containing the number of bins for each dimension.

            title (string): the title of the histogram.
    """
    def __init__(self, dim: int, minBin: Sequence, maxBin: Sequence, nBins: Sequence, title=str()):
        self._dim = dim  # number of dimensions
        self._title = title  # the title of the histogram.

        self._entries = 0  # total number of entries
        self._entriesUnderflow = 0
        self._entriesOverflow = 0
        self._sumWeights = 0  # Total Sum of weights
        self._sumWeights2 = 0  # Total Sum of weight*weight

        self._sumWeightsX = []  # Total Sum of weight*X for each dimension
        self._sumWeightsX2 = []  # Total Sum of weight*X*X for each dimension

        self._axes = []  # a list of axes. 1 axis per each dimension
        self._sizeOverDims = []  # an array of sizes useful for converting to coordinates of linear array of cells
        n_cells = 1
        for i in range(dim):
            binsLeftEdges = np.linspace(minBin[i], maxBin[i], nBins[i], endpoint=False)
            x = np.append(binsLeftEdges, maxBin[i])
            self._axes.append(HistAxis(x))
            self._sumWeightsX.append(.0)
            self._sumWeightsX2.append(.0)
            self._sizeOverDims.append(n_cells)
            n_cells = n_cells * nBins[i]

        self._nCells = n_cells  # total number of cells (global linear bins)
        self._binsEntries = []  # contains the values/entries per cell (global linear bins)
        self._binSumWeightsValues2 = []  # array of sum of squared weights per cell (global linear bins)
        for i in range(n_cells):
            self._binsEntries.append(.0)
            self._binSumWeightsValues2.append(.0)

    @property
    def dimension(self):
        """number of dimensions """
        return self._dim

    @property
    def title(self):
        """ the title of the histogram """
        return self._title

    @title.setter
    def title(self, t: str):
        """ sets the title of the histogram """
        self._title = t

    @property
    def entries(self):
        """ total number of entries """
        return self._entries

    @property
    def cells(self):
        """total number of cells (global linear bins)"""
        return self._nCells

    @property
    def sum_of_weights(self):
        """Total Sum of weights"""
        return self._sumWeights

    @property
    def sum_of_weights2(self):
        """Total Sum of weights squared"""
        return self._sumWeights2

    @property
    def sum_of_weightsX(self):
        """ a list of total sum of weights*X for each dimension"""
        return self._sumWeightsX

    @property
    def sum_of_weightsX2(self):
        """a list of total sum of weights*X*X for each dimension"""
        return self._sumWeightsX2

    def get_axes_list(self) -> List[HistAxis]:
        """ a list of axes """
        return self._axes

    def get_axis(self, i: int) -> HistAxis:
        """get the axis for dimension 'i' """
        return self._axes[i]

    def cell_to_bins(self, idx_cell: int) -> List[int]:
        """ Converts cell index to indexes of bins.

        returns a list of bin indexes on the axes that refer to this cell "idx_cell"

        Args:
            idx_cell (int): the cell indexes.

        Returns:
            List[int]. A length of the same as the histogram dimension

        See Also:
            :py:meth:`bins_to_cell`, :py:meth:`pos_to_cell`
        """
        idxBins = []
        if 0 <= idx_cell < self.cells:
            for k in range(self.dimension):
                idxBins.append(int((idx_cell/self._sizeOverDims[k]) % self.get_axis(k).nbins))

        return idxBins

    def bins_to_cell(self, idxBins: Sequence) -> int:
        """ Converts bin indexes to global linear bin (cell) index.

        Returns the index of the cell that is located by the bin indexes on the axes

        Args:
            idxBins (Sequence): the bin indexes of the axis. Its length must be the same as the histogram dimension

        Returns:
            int. The cell index (global linear bin index)

        See Also:
            :py:meth:`cell_to_bins`, :py:meth:`pos_to_cell`
        """
        idx_cell = 0
        for i in range(self.dimension):
            idx_cell += self._sizeOverDims[i] * idxBins[i]

        return idx_cell

    def pos_to_cell(self, x: Sequence) -> int:
        """ Converts coordinate positions to global linear bin (cell) index.

        Returns the cell index (global linear bin) that contains the point at position 'x'. Where 'x' are the
        coordinates of a point in :py:meth:`dimension`.

        Args:
            x (Sequence): a valid point in the space of histogram

        Returns:
            int. If there is no such bin a -1 is returned.

        See Also:
            :py:meth:`bins_to_cell`, :py:meth:`cell_to_bins`
        """
        bin_coords = []
        xL = len(x)
        for d in range(self.dimension):
            if d >= xL:
                bin_coords.append(0)
            else:
                bin_idx = self.get_axis(d).get_bin(x[d])
                if bin_idx == -1:
                    return -1
                else:
                    bin_coords.append(bin_idx)

        return self.bins_to_cell(bin_coords)

    def get_bins_edges(self, includeEmptyBins: bool=False) -> List[List[float]]:
        """ Returns all bins per each dimension (axis).  By default it **does not** include empty cells.

        The list contains for each dimension the list of minimum edges for each cell (global linear bin)

        Args:
            includeEmptyBins (bool): if empty bins are included in the list. If True then empty bins are included,
                otherwise they are NOT included

        Returns:
            list of list.
        """
        result = []
        if includeEmptyBins:  # include all bins (including the empty ones)
            for d in range(self.dimension):
                result.append(self.get_axis(d).get_bins())
        else:
            for d in range(self.dimension):
                result.append([])

            for icell in range(self.cells):
                cell_value = self.get_cell_content(icell)
                if cell_value != 0.0:
                    idxBins = self.cell_to_bins(icell)
                    for d, ibin in enumerate(idxBins):
                        result[d].append(self.get_axis(d).get_bin_lower_edge(ibin))

        return result

    def get_bins_centers(self, includeEmptyBins: bool=False) -> List[List[float]]:
        """ Returns the positions of the centers of all bins per each dimension (axis).
        By default it **does not** include empty cells.

        Args:
            includeEmptyBins (bool): if empty bins are included in the list. If True then empty bins are included,
                otherwise they are NOT included

        Returns:
            list of list.
        """
        result = []
        if includeEmptyBins:  # include all bins (including the empty ones)
            for d in range(self.dimension):
                result.append(self.get_axis(d).get_bins_centers())
        else:
            for d in range(self.dimension):
                result.append([])

            for icell in range(self.cells):
                cell_value = self.get_cell_content(icell)
                if cell_value != 0.0:
                    idxBins = self.cell_to_bins(icell)
                    for d, ibin in enumerate(idxBins):
                        result[d].append(self.get_axis(d).get_bin_center(ibin))

        return result

    def get_cell_content(self, i: int) -> float:
        """ Returns the content of the cell 'i' or the value of Underflow (if i<0) or Overflow (if i>= # of cells)

        Args:
            i (int): a valid cell index (aka global linear bin)

        Returns:
            float or 0.0 if the position is outside cells ranges
        """
        if i < 0:
            return self._entriesUnderflow

        if i >= self.cells:
            return self._entriesOverflow

        return self._binsEntries[i]

    def get_cells_contents(self, includeEmptyBins=False) -> List[float]:
        """ Returns the contents of all bins (cells) per each dimension.  By default it **does not** include empty cells.

       Args:
           includeEmptyBins (bool): if empty bins are included in the list. If True then empty bins are included,
                otherwise they are NOT included

       Returns:
           list of list.
       """
        result = []
        if includeEmptyBins:
            return self._binsEntries
        else:
            for icell in range(self.cells):
                cell_value = self.get_cell_content(icell)
                if cell_value != 0.0:
                    result.append(cell_value)

        return result

    def get_pos_content(self, x: Sequence) -> float:
        """Returns the content of the cell located at position x

        Args:
            x (Sequence): a position array

        Returns:
            float or 0.0 if the position is outside bin ranges
        """
        return self.get_cell_content(self.pos_to_cell(x))

    def get_cell_content_error(self, i: int) -> float:
        """Returns the error value associated with cell 'i'

        Args:
            i (int): a valid cell index (aka global linear bin)

        The error is computed as follows:
            - sqrt(Sum of squared weights): If weights were used during fill
            - sqrt(bin content): If weights were NOT used during fill

        Returns:
            float.
        """
        result = 0.0
        if self._sumWeights2 >= 0.0:
            result = self._binSumWeightsValues2[i]
        else:
            result = self._binsEntries[i]
        return math.sqrt(result)

    def get_cells_contents_errors(self, includeEmptyBins=False) -> List[float]:
        """ Returns a list containing the errors associated to each cell.
        By default it **does not** include empty cells.

        Args:
            includeEmptyBins (bool): if empty cell are included in the list. If True then empty cell are included,
                otherwise they are NOT included

        Returns:
            list.
        """
        result = []
        if includeEmptyBins:
            for i_cell in range(self.cells):
                bin_err = self.get_cell_content_error(i_cell)
                result.append(bin_err)
        else:
            for i_cell in range(self.cells):
                cell_value = self.get_cell_content(i_cell)
                if cell_value != 0.0:
                    bin_err = self.get_cell_content_error(i_cell)
                    result.append(bin_err)
        return result

    def get_stats(self) -> Dict[str, float]:
        """ Returns general statistics about the histogram.

            A dictionary with the keys: "Entries", "SumWeights", "SumWeights2", "SumWeightsX", "SumWeightsX2"

         Returns:
            Dict{str,Any}.
         """
        return {"Entries": self._entries,
                "Underflow": self._entriesUnderflow,
                "Overflow": self._entriesOverflow,
                "SumWeights": self._sumWeights,
                "SumWeights2": self._sumWeights2,
                "SumWeightsX": self._sumWeightsX,
                "SumWeightsX2": self._sumWeightsX2
                }

    def projection(self, keepDims: Sequence):
        """ Project this Histogram to another Histogram keeping the axis defined in `keepDims`

        Args:
            keepDims (Sequence): an array that contains the id's of the dimensions to keep when projecting.
                The number of dimensions of the projected histogram is the length of `keepDims`

        Returns:
            HistND. The projected histogram.
        """
        # keep_dims = sorted(keepDims)
        keep_dims = keepDims

        minBins = []
        maxBins = []
        nBins = []
        for kdim in keep_dims:
            minBins.append(self.get_axis(kdim).minBin)
            maxBins.append(self.get_axis(kdim).maxBin)
            nBins.append(self.get_axis(kdim).nbins)

        result = HistND(len(keep_dims), minBins, maxBins, nBins, title="Projection of " + self.title)

        for i_cell in range(self.cells):
            value = self.get_cell_content(i_cell)
            idx_bins = self.cell_to_bins(i_cell)  # has length 'self.dimension'
            bins = []
            for kdim in keep_dims:
                    bins.append(idx_bins[kdim])
            result.fill_bins(bins, weight=value)

        return result

    def fill_cell(self, i_cell: int, value: float=None, weight: float=1.0, error_per_bin=True) -> int:
        """ Fill the histogram using global cell index.

        Args:
            i_cell (int): the global bin index (cell index).

            weight (float): the weight to fill in. Defaults to 1.0

            value (float): a value to fill in the cell. This argument is used in Profiles, ignore it for Histograms.

            error_per_bin (bool): whether to compute weights per bins.
        
        Warning: 
            This is expensive operation because it computes the bins indexes (it decomposes cell index) and positions
            per axis before filling weights per bin. Its Recommended to use other fill_* methods

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
            are not valid (underflow or overflow)

        See Also:
            :py:meth:`fill_pos`, :py:meth:`fill_bins`

        """
        # sane check
        if i_cell < 0:
            self._entriesUnderflow += 1
            return -1

        if i_cell > self.cells - 1:
            self._entriesOverflow += 1
            return -1

        # we got a valid bin
        self._binSumWeightsValues2[i_cell] += weight * weight
        self._binsEntries[i_cell] += weight

        self._entries += 1
        self._sumWeights += weight
        self._sumWeights2 += weight * weight

        if error_per_bin:  # expensive operations. use other fill_* methods
            idx_bins = self.cell_to_bins(i_cell)
            for d, id_bin in enumerate(idx_bins):
                x = self.get_axis(d).get_bin_center(id_bin)
                self._sumWeightsX[d] += weight * x
                self._sumWeightsX2[d] += weight * x * x

        return i_cell

    def fill_bins(self, arr: Sequence, value: float=None, weight: float=1.0) -> int:
        """ Fill the histogram using bin indexes.

        Args:
            arr (Sequence): the bin indexes for each dimension. The size of the array is the same as the number of
                dimensions

            weight (float): the weight to fill in

            value (float): a value to fill in the cell. This argument is used in Profiles, ignore it for Histograms.

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
                are not valid

        NOTE:
            b contains indexes of the bins on each axis, not the positions on axis

        See Also:
            :py:meth:`fill_pos`, :py:meth:`fill_cell`
        """
        i_cell = self.bins_to_cell(arr)

        if self.fill_cell(i_cell, weight=weight, error_per_bin=False) != i_cell:  # we got underflow or overflow
            return -1

        for d, id_bin in enumerate(arr):
            x = self.get_axis(d).get_bin_center(id_bin)
            self._sumWeightsX[d] += weight * x
            self._sumWeightsX2[d] += weight * x * x

        return i_cell

    def fill_pos(self, x: Sequence, value: float=None, weight: float=1.0) -> int:
        """ Fill the histogram using a position.

        Args:
            x (Sequence): the coordinates on the axis of a cell. The size of the array is the same as the number of
                dimensions

            weight (float): the weight to fill in. Defaults to 1.0

            value (float): a value to fill in the cell. This argument is used in Profiles, ignore it for Histograms.

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
        are not valid

        NOTE:
            x contains coordinates not indexes of the bins

        See Also:
            :py:meth:`fill_cell`, :py:meth:`fill_bins`
        """
        i_cell = self.pos_to_cell(x)

        if self.fill_cell(i_cell, weight=weight, error_per_bin=False) != i_cell:   # we got underflow or overflow
            return -1

        for d in range(self.dimension):
            self._sumWeightsX[d] += weight * x[d]
            self._sumWeightsX2[d] += weight * x[d] * x[d]

        return i_cell

    def fill(self, x: float=None, y: float=None, z: float=None, arr: Sequence=None, value: float=None,
             weight: float=1.0) -> int:
        """ Fill the histogram.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D histograms.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D histograms.

            z (float): the coordinate on the third axis of the histogram. Used only 3D histograms.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
                If using arr the function will ignore the arguments x,y,z. This argument is used when having
                histograms higher then 3D. Its length must be the same as the histogram dimension.

            value (float): a value to fill in the cell. This argument is only used by Profiles, ignore it when filling
                histograms.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
            are not valid

        NOTE:
            Use the position **arr** OR the coordinates x,y,z. If arr is not None, then the function uses it. Otherwise
            it uses the coordinates x, y, z.

        See Also:
            :py:meth:`fill_cell`, :py:meth:`fill_bins`
        """
        if arr is not None:
            return self.fill_pos(arr, weight=weight)

        else:  # arr is None
            switcher = {
                1: [x],
                2: [x, y],
                3: [x, y, z]
            }

            pos = switcher.get(self.dimension)

            return self.fill_pos(pos, weight=weight)

    def intersect(self, other):
        """ intersection of 2 histograms

        Args:
            other: another histogram

        Returns:
            another histogram that represent the reunion of these 2 histograms
        """
        n_dims = min(self.dimension, other.dimension)

        n_minBins = []
        n_maxBins = []
        n_nBins = []
        for d in range(n_dims):
            n_minBins.append(min(self.get_axis(d).minBin, other.get_axis(d).minBin))
            n_maxBins.append(max(self.get_axis(d).maxBin, other.get_axis(d).maxBin))
            n_density = max(self.get_axis(d).density(), other.get_axis(d).density())
            n_nBins.append(int(n_density * (n_maxBins[d] - n_minBins[d])))

        for d in range(n_dims, self.dimension):
            n_minBins.append(self.get_axis(d).minBin)
            n_maxBins.append(self.get_axis(d).maxBin)
            n_nBins.append(self.get_axis(d).nbins)

        result = HistND(self.dimension, n_minBins, n_maxBins, n_nBins)

        for i_cell in range(result.cells):
            idx_bins = result.cell_to_bins(i_cell)

            pos = []
            for d, id_bin in enumerate(idx_bins):
                pos.append(result.get_axis(d).get_bin_center(id_bin))

            val1 = self.get_pos_content(pos)
            val2 = other.get_pos_content(pos)

            result.fill_cell(i_cell, weight=val1 + val2)

        return result

    def scale(self, factor: float, scale_errors: bool=False):
        """ Scales the histograms.

        The values of all cells are multiplied by 'factor'

        Args:
            factor (float): the value to scale the histogram

            scale_errors (bool): if true then it also scales the errors per dimension

        Returns:
            none.
        """
        scaledHist = self

        for i_cell in range(scaledHist.cells):
            scaledHist._binSumWeightsValues2[i_cell] = factor * scaledHist._binSumWeightsValues2[i_cell]
            scaledHist._binsEntries[i_cell] = factor * scaledHist._binsEntries[i_cell]

            scaledHist._sumWeights = factor * scaledHist._sumWeights
            scaledHist._sumWeights2 = factor * factor * scaledHist._sumWeights2

        if scale_errors:
            for d in range(scaledHist.dimension):
                scaledHist._sumWeightsX[d]  = factor * scaledHist._sumWeightsX[d]
                scaledHist._sumWeightsX2[d] = factor * scaledHist._sumWeightsX2[d]
        
        return self

    def __add__(self, other):
        """Adds 2 histograms

        Args:
            other (HistND): another histogram, not necessary of the same dimension.

        Returns:
            HistND. The sum of the 2 histograms

        """
        n_dims = min(self.dimension, other.dimension)

        n_minBins = []
        n_maxBins = []
        n_nBins = []
        for d in range(n_dims):
            n_minBins.append(min(self.get_axis(d).minBin, other.get_axis(d).minBin))
            n_maxBins.append(max(self.get_axis(d).maxBin, other.get_axis(d).maxBin))
            n_density = self.get_axis(d).density()
            n_nBins.append(int(n_density * (n_maxBins[d] - n_minBins[d])))

        for d in range(n_dims, self.dimension):
            n_minBins.append(self.get_axis(d).minBin)
            n_maxBins.append(self.get_axis(d).maxBin)
            n_nBins.append(self.get_axis(d).nbins)

        result = HistND(self.dimension, n_minBins, n_maxBins, n_nBins)

        for i_cell in range(result.cells):
            idx_bins = result.cell_to_bins(i_cell)

            pos = []
            for d, id_bin in enumerate(idx_bins):
                pos.append(result.get_axis(d).get_bin_center(id_bin))

            val1 = self.get_pos_content(pos)
            val2 = other.get_pos_content(pos)

            result.fill_cell(i_cell, val1 + val2)

        return result

    def __sub__(self, other):
        """Substract 2 histograms

        Args:
            other (HistND): another histogram, not necessary of the same dimension.

        Returns:
            HistND. The difference of the 2 histograms
        """
        n_dims = min(self.dimension, other.dimension)

        n_minBins = []
        n_maxBins = []
        n_nBins = []
        for d in range(n_dims):
            n_minBins.append(min(self.get_axis(d).minBin, other.get_axis(d).minBin))
            n_maxBins.append(max(self.get_axis(d).maxBin, other.get_axis(d).maxBin))
            n_density = self.get_axis(d).density()
            n_nBins.append(int(n_density * (n_maxBins[d] - n_minBins[d])))

        for d in range(n_dims, self.dimension):
            n_minBins.append(self.get_axis(d).minBin)
            n_maxBins.append(self.get_axis(d).maxBin)
            n_nBins.append(self.get_axis(d).nbins)

        result = HistND(self.dimension, n_minBins, n_maxBins, n_nBins)

        for i_cell in range(result.cells):
            idx_bins = result.cell_to_bins(i_cell)

            pos = []
            for d, id_bin in enumerate(idx_bins):
                pos.append(result.get_axis(d).get_bin_center(id_bin))

            val1 = self.get_pos_content(pos)
            val2 = other.get_pos_content(pos)

            result.fill_cell(i_cell, weight=val1 - val2)

        return result

    def __mul__(self, other):
        """Multiply 2 histograms

        Args:
            other (HistND): a histogram of the same dimension.

        Returns:
            HistND. The multiplication of the 2 histograms
        """
        n_dims = min(self.dimension, other.dimension)

        n_minBins = []
        n_maxBins = []
        n_nBins = []
        for d in range(n_dims):
            n_minBins.append(min(self.get_axis(d).minBin, other.get_axis(d).minBin))
            n_maxBins.append(max(self.get_axis(d).maxBin, other.get_axis(d).maxBin))
            n_density = self.get_axis(d).density()
            n_nBins.append(int(n_density * (n_maxBins[d] - n_minBins[d])))

        for d in range(n_dims, self.dimension):
            n_minBins.append(self.get_axis(d).minBin)
            n_maxBins.append(self.get_axis(d).maxBin)
            n_nBins.append(self.get_axis(d).nbins)

        result = HistND(self.dimension, n_minBins, n_maxBins, n_nBins)

        for i_cell in range(result.cells):
            idx_bins = result.cell_to_bins(i_cell)

            pos = []
            for d, id_bin in enumerate(idx_bins):
                pos.append(result.get_axis(d).get_bin_center(id_bin))

            val1 = self.get_pos_content(pos)
            val2 = other.get_pos_content(pos)

            result.fill_cell(i_cell, weight=val1 * val2)

        return result

    def __truediv__(self, other):
        """Divide 2 histograms

        Args:
            other (HistND): a histogram of the same dimension.

        Returns:
            HistND. The sum of the 2 histograms
        """
        n_dims = min(self.dimension, other.dimension)

        n_minBins = []
        n_maxBins = []
        n_nBins = []
        for d in range(n_dims):
            n_minBins.append(min(self.get_axis(d).minBin, other.get_axis(d).minBin))
            n_maxBins.append(max(self.get_axis(d).maxBin, other.get_axis(d).maxBin))
            n_density = self.get_axis(d).density()
            n_nBins.append(int(n_density * (n_maxBins[d] - n_minBins[d])))

        for d in range(n_dims, self.dimension):
            n_minBins.append(self.get_axis(d).minBin)
            n_maxBins.append(self.get_axis(d).maxBin)
            n_nBins.append(self.get_axis(d).nbins)

        result = HistND(self.dimension, n_minBins, n_maxBins, n_nBins)

        for i_cell in range(result.cells):
            idx_bins = result.cell_to_bins(i_cell)

            pos = []
            for d, id_bin in enumerate(idx_bins):
                pos.append(result.get_axis(d).get_bin_center(id_bin))

            val1 = self.get_pos_content(pos)
            val2 = other.get_pos_content(pos)
            if val2 == 0:
                result.fill_cell(i_cell, weight=0)
            else:
                result.fill_cell(i_cell, weight=val1 / val2)

        return result

    def integral(self, minCellId: int=0, maxCellId: int=None) -> float:
        """ Computes integral over cells range '[minCellId, maxCellId]'

        The integral is the sum over all cells of the product of cell's content and the volume described by its bins:
            I = Sum_i CELL_CONTENT dx * dy * dz * ... dXn

        Args:
            minCellId (int): minimum cell id.
                Default it is 0 (zero).

            maxCellId (int): maximum cell id.
                default is None, meaning all cells

        Returns:
            float.

        See Also:
            :py:meth:`integral_over_bins`, :py:meth:`integral_over_pos`
        """
        a = minCellId
        b = maxCellId

        if maxCellId is None:
            b = self.cells

        if 0 > a or a > self.cells:
            raise ValueError("minCellId can not be negative or bigger then the maximum cells")

        if 0 > b or b > self.cells:
            raise ValueError("maxCellId can not be negative or bigger then the maximum cells")

        if a >= b:
            warnings.warn("minCellId is bigger or equal to the maxCellId. Returning zero..")
            return 0.0

        result = 0.0
        for i_cell in range(a, b):
            value = self.get_cell_content(i_cell)
            cellBins = self.cell_to_bins(i_cell)
            volume = 1.0
            for d, b in enumerate(cellBins):
                volume = volume * self.get_axis(d).get_bin_width(b)
            result += value * volume
        return result

    def integral_over_bins(self, minBinsIds: Sequence, maxBinsIds: Sequence) -> float:
        """ Computes integral over bins range

        Args:
            minBinsIds (Sequence): an array of ints containing the minimum bins over each dimension

            maxBinsIds (Sequence): an array of ints containing the maximum bins over each dimension

        Returns:
            float.

        See Also:
            :py:meth:`integral`, :py:meth:`integral_over_pos`
        """
        min_cell_id = self.bins_to_cell(minBinsIds)
        max_cell_id = self.bins_to_cell(maxBinsIds)

        return self.integral(min_cell_id, max_cell_id)

    def integral_over_pos(self, minPos: Sequence, maxPos: Sequence) -> float:
        """ Computes integral between 2 positions.

        Args:
            minPos (Sequence): an array of floats containing the minimum position on each dimension

            maxPos (Sequence): an array of floats containing the maximum position on each dimension

        Returns:
            float.

        See Also:
            :py:meth:`integral`, :py:meth:`integral_over_pos`
        """
        min_cell_id = self.pos_to_cell(minPos)
        max_cell_id = self.pos_to_cell(maxPos)

        return self.integral(min_cell_id, max_cell_id)


class Hist1D(HistND):
    """ A 1-Dimensional Histogram

    Args:
        minBin (float): the minimum value of lower edge of bins

        maxBin (float): the maximum value of upper edge of bins

        nBins (integer): the number of bins

        title (string): the title of the histogram
    """
    def __init__(self, nBins: int, minBin: float, maxBin: float, title=str()):
        HistND.__init__(self, 1, [minBin], [maxBin], [nBins], title)

    def fill(self, x: float=None, y: float=None, z: float=None, arr: Sequence=None, value: float=None,
             weight: float=1.0) -> int:
        """ Fill the histogram.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D histograms.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D histograms.

            z (float): the coordinate on the third axis of the histogram. Used only 3D histograms.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
                If using arr the function will ignore the arguments x,y,z. This argument is used when having
                histograms higher then 3D. Its length **must be** the same as the histogram dimension, it is not checked

            value (float): a value to fill in the cell. This argument is only used by Profiles, ignore it when filling
                histograms.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
            are not valid

        NOTE:
           This overridden method use arr if it is not None. Otherwise it only uses argument x and the rest arguments
            are ignored.

        See Also:
            :py:meth:`HistND.fill_cell`, :py:meth:`HistND.fill_bins`, :py:meth:`HistND.fill_pos`
        """
        if arr is not None:
            return super(Hist1D, self).fill(arr=arr, weight=weight)

        # arr is None
        if x is None:
            raise ValueError("Requires a valid value for x different then None")

        if y is not None or z is not None:
            warnings.warn("Second and third arguments are not supported for 1D histograms. Ignoring arguments y and z..")

        return super(Hist1D, self).fill(x, weight=weight)


class Hist2D(HistND):
    """ A 2-Dimensional Histogram

    Args:
        nBinsX (integer): the number of bins on the X-axis

        minBinX (float): the minimum value of lower edge of bins on the X-axis

        maxBinX (float): the maximum value of upper edge of bins on the X-axis

        nBinsY (integer): the number of bins on the Y-axis

        minBinY (float): the minimum value of lower edge of bins on the Y-axis

        maxBinY (float): the maximum value of upper edge of bins on the Y-axis

        title (string): the title of the histogram
    """
    def __init__(self, nBinsX, minBinX, maxBinX, nBinsY, minBinY, maxBinY, title=str()):
        HistND.__init__(self, 2, [minBinX, minBinY], [maxBinX, maxBinY], [nBinsX, nBinsY], title)

    def fill(self, x: float=None, y: float=None, z: float=None, arr: Sequence=None, value: float=None,
             weight: float=1.0) -> int:
        """ Fill the histogram.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D histograms.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D histograms.

            z (float): the coordinate on the third axis of the histogram. Used only 3D histograms.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
                If using arr the function will ignore the arguments x,y,z. This argument is used when having
                histograms higher then 3D. Its length **must be** the same as the histogram dimension.

            value (float): a value to fill in the cell. This argument is only used by Profiles, ignore it when filling
                histograms.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
            are not valid

        NOTE:
            This overridden method use arr if it is not None. Otherwise it only uses arguments x and y. The rest arguments
            are ignored.

        See Also:
            :py:meth:`HistND.fill_cell`, :py:meth:`HistND.fill_bins`, :py:meth:`HistND.fill_pos`
        """
        if arr is not None:
            return super(Hist2D, self).fill(arr=arr, weight=weight)

        # arr is None
        if x is None:
            raise ValueError("Requires a valid value for x different then None")

        if y is None:
            raise ValueError("Requires a valid value for y different then None")

        if z is not None:
            warnings.warn("Third argument is not supported for 2D histograms. Ignoring arguments 'z'..")

        return super(Hist2D, self).fill(x, y, weight=weight)

    def projectionX(self):
        """ Project this histogram on the X-axis

        Returns:
            HistND. The projected histogram has dimension 1.
        """
        return self.projection([0])

    def projectionY(self):
        """ Project this histogram on the Y-axis

         Returns:
            HistND. The projected histogram has dimension 1.
        """
        return self.projection([1])


class Hist3D(HistND):
    """ A 3-Dimensional Histogram

    Args:
        nBinsX (integer): the number of bins on the X-axis

        minBinX (float): the minimum value of lower edge of bins on the X-axis

        maxBinX (float): the maximum value of upper edge of bins on the X-axis

        nBinsY (integer): the number of bins on the Y-axis

        minBinY (float): the minimum value of lower edge of bins on the Y-axis

        maxBinY (float): the maximum value of upper edge of bins on the Y-axis

        nBinsZ (integer): the number of bins on the Z-axis

        minBinZ (float): the minimum value of lower edge of bins on the Z-axis

        maxBinZ (float): the maximum value of upper edge of bins on the Z-axis

        title (string): the title of the histogram
    """
    def __init__(self, nBinsX, minBinX, maxBinX, nBinsY, minBinY, maxBinY, nBinsZ, minBinZ, maxBinZ, title=str()):
        HistND.__init__(self, 3, [minBinX, minBinY, minBinZ], [maxBinX, maxBinY, maxBinZ], [nBinsX, nBinsY, nBinsZ],
                        title)

    def fill(self, x: float = None, y: float = None, z: float = None, arr: Sequence = None, value: float = None,
             weight: float = 1.0) -> int:
        """ Fill the histogram.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D histograms.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D histograms.

            z (float): the coordinate on the third axis of the histogram. Used only 3D histograms.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
                If using arr the function will ignore the arguments x,y,z. This argument is used when having
                histograms higher then 3D. Its length **must be** the same as the histogram dimension.

            value (float): a value to fill in the cell. This argument is only used by Profiles, ignore it when filling
                histograms.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
            are not valid

        NOTE:
            This overridden method use arr if it is not None. Otherwise it only uses arguments x and y. The rest arguments
            are ignored.

        See Also:
            :py:meth:`HistND.fill_cell`, :py:meth:`HistND.fill_bins`, :py:meth:`HistND.fill_pos`
        """
        if arr is not None:
            return super(Hist3D, self).fill(arr=arr, weight=weight)

        # arr is None
        if x is None:
            raise ValueError("Requires a valid value for x different then None")

        if y is None:
            raise ValueError("Requires a valid value for y different then None")

        if z is None:
            raise ValueError("Requires a valid value for z different then None")

        return super(Hist3D, self).fill(x, y, z, weight=weight)

    def projectionX(self):
        """ Project this histogram on the X-axis

        Returns:
            HistND. The projected histogram has dimension 1.
        """
        return self.projection([0])

    def projectionY(self):
        """ Project this histogram on the Y-axis

         Returns:
            HistND. The projected histogram has dimension 1.
        """
        return self.projection([1])

    def projectionZ(self):
        """ Project this histogram on the Z-axis

         Returns:
            HistND. The projected histogram has dimension 1.
        """
        return self.projection([1])

    def projectionXY(self):
        """ Project this histogram on the X-axis and Y-axis

        Returns:
            HistND. The projected histogram has dimension 2.
        """
        return self.projection([0, 1])

    def projectionXZ(self):
        """ Project this histogram on the X-axis and Z-axis

        Returns:
            HistND. The projected histogram has dimension 2.
        """
        return self.projection([0, 2])

    def projectionYZ(self):
        """ Project this histogram on the Y-axis and Z-axis

        Returns:
            HistND. The projected histogram has dimension 2.
        """
        return self.projection([1, 2])
