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
import numpy as np
from typing import List, Dict
from bisect import bisect_left

__all__ = 'HistAxis', 'HistND', 'Hist1D', 'Hist2D', 'Hist3D'


class HistAxis:
    """ An axis for use in constructing histograms

    Args:
        bins (array-like): an ordered (ascending order) array of floats containing the lower edges of the bins

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
            return 0.0

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

    def get_bins(self) -> List[float]:
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

            minBin (array like): an array containing the minimum value of lower (leftmost) edge of bins for each dimension.

            maxBin (array like): an array containing the maximum value of upper (rightmost) edge of bins for each dimension.

            nBins (array like):  an array containing the number of bins for each dimension.

            title (string): the title of the histogram.
    """
    def __init__(self, dim: int, minBin, maxBin, nBins, title=str()):
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
        self._binSumWeightsVals2 = []  # array of sum of squared weights per cell (global linear bins)
        for i in range(n_cells):
            self._binsEntries.append(.0)
            self._binSumWeightsVals2.append(.0)

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

    def bins_to_cell(self, idxBins) -> int:
        """ Converts bin indexes to global linear bin (cell) index.

        Returns the index of the cell that is located by the bin indexes on the axes

        Args:
            idxBins (array-like): the bin indexes of the axis. Its length must be the same as the histogram dimension

        Returns:
            int. The cell index (global linear bin index)

        See Also:
            :py:meth:`cell_to_bins`, :py:meth:`pos_to_cell`
        """
        idx_cell = 0
        for i in range(self.dimension):
            idx_cell += self._sizeOverDims[i] * idxBins[i]

        return idx_cell

    def pos_to_cell(self, x) -> int:
        """ Converts coordinate positions to global linear bin (cell) index.

        Returns the cell index (global linear bin) that contains the point at position 'x'. Where 'x' are the coordinates of a point in :py:meth:`dimension`.

        Args:
            x (array-like): a valid point in the space of histogram

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
            includeEmptyBins (bool): if empty bins are included in the list. If True then empty bins are included, otherwise they are NOT included

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
            includeEmptyBins (bool): if empty bins are included in the list. If True then empty bins are included, otherwise they are NOT included

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
        """ Returns the content of the cell 'i'

        Args:
            i (int): a valid cell index (aka global linear bin)

        Returns:
            float or 0.0 if the position is outside cells ranges
        """
        if i < 0 or i >= self.cells:
            return 0.0

        return self._binsEntries[i]

    def get_cells_contents(self, includeEmptyBins=False) -> List[float]:
        """ Returns the contents of all bins (cells) per each dimension.  By default it **does not** include empty cells.

       Args:
           includeEmptyBins (bool): if empty bins are included in the list. If True then empty bins are included, otherwise they are NOT included

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

    def get_pos_content(self, x) -> float:
        """Returns the content of the cell located at position x

        Args:
            x (array-like): a position array

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
            result = self._binSumWeightsVals2[i]
        else:
            result = self._binsEntries[i]
        return math.sqrt(result)

    def get_cells_contents_errors(self, includeEmptyBins=False) -> List[float]:
        """ Returns a list containing the errors associated to each cell.
        By default it **does not** include empty cells.

        Args:
            includeEmptyBins (bool): if empty cell are included in the list. If True then empty cell are included, otherwise they are NOT included

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

    def projection(self, keepDims):
        """ Project this Histogram to another Histogram keeping the axis defined in `keepDims`

        Args:
            keepDims (array-like): an array that contains the id's of the dimensions to keep when projecting.  The number of dimensions of the projected histogram is the length of `keepDims`

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
            result.fill_bins_w(bins, value)

        return result

    def fill_cell(self, i_cell: int, do_error_per_bin=True) -> int:
        """ Fill the histogram (no weight).

        Args:
            i_cell (int): the global bin index (cell index).

            do_error_per_bin (bool): whether to compute weights per bins.
        
        Warning: 
            This is expensive operation because it computes the bins indexes (it decomposes cell index) and positions per axis before filling weights per bin.
            Its Recommended to use other fill_* methods

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

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
        self._binSumWeightsVals2[i_cell] += 1.0
        self._binsEntries[i_cell] += 1

        self._entries += 1
        self._sumWeights += 1
        self._sumWeights2 += 1

        if do_error_per_bin:
            idx_bins = self.cell_to_bins(i_cell)
            for d, id_bin in enumerate(idx_bins):
                x = self.get_axis(d).get_bin_center(id_bin)
                self._sumWeightsX[d] += x
                self._sumWeightsX2[d] += x * x

        return i_cell

    def fill_cell_w(self, i_cell: int, w: float, do_error_per_bin=True) -> int:
        """ Fill the histogram with weight.

        Args:
            i_cell (int): the global bin index (cell index).

            w (float): the weight to fill in

            do_error_per_bin (bool): whether to compute weights per bins.
        
        Warning: 
            This is expensive operation because it computes the bins indexes (it decomposes cell index) and positions per axis before filling weights per bin.
            Its Recommended to use other fill_* methods.

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        See Also:
            :py:meth:`fill_pos_w`, :py:meth:`fill_bins_w`
        """
        # sane check
        if i_cell < 0:
            self._entriesUnderflow += 1
            return -1

        if i_cell > self.cells-1:
            self._entriesOverflow += 1
            return -1

        # we got a valid bin
        self._binSumWeightsVals2[i_cell] += w * w
        self._binsEntries[i_cell] += w

        self._entries += 1
        self._sumWeights += w
        self._sumWeights2 += w * w

        if do_error_per_bin:  # expensive operations. use other fill_* methods
            idx_bins = self.cell_to_bins(i_cell)
            for d, id_bin in enumerate(idx_bins):
                x = self.get_axis(d).get_bin_center(id_bin)
                self._sumWeightsX[d] += w * x
                self._sumWeightsX2[d] += w * x * x

        return i_cell

    def fill_bins(self, b) -> int:
        """ Fill the histogram no weight.

        Args:
            b (array-like): the bin indexes for each dimension. The size of the array is the same as the number of dimensions

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        Note:
            b contains indexes of the bins on each axis, not the positions on axis

        See Also:
            :py:meth:`fill_pos`, :py:meth:`fill_cell`
        """
        i_cell = self.bins_to_cell(b)

        if self.fill_cell(i_cell, False) != i_cell:
            return -1

        for d, id_bin in enumerate(b):
            x = self.get_axis(d).get_bin_center(id_bin)
            self._sumWeightsX[d] += x
            self._sumWeightsX2[d] += x * x

        return i_cell

    def fill_bins_w(self, b, w: float) -> int:
        """ Fill the histogram with weight.

        Args:
            b (array-like): the bin indexes for each dimension. The size of the array is the same as the number of dimensions

            w (float): the weight to fill in

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        NOTE:
            b contains indexes of the bins on each axis, not the positions on axis

        See Also:
            :py:meth:`fill_pos`, :py:meth:`fill_cell`
        """
        i_cell = self.bins_to_cell(b)

        if self.fill_cell_w(i_cell, w, False) != i_cell:
            return -1

        for d, id_bin in enumerate(b):
            x = self.get_axis(d).get_bin_center(id_bin)
            self._sumWeightsX[d] += w * x
            self._sumWeightsX2[d] += w * x * x

        return i_cell

    def fill_pos(self, x) -> int:
        """ Fill the histogram (no weights).

        Args:
            x (array-like): the coordinates on the axis of a cell. The size of the array is the same as the number of dimensions

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid 

        NOTE:
            x contains coordinates not indexes of the bins

        See Also:
            :py:meth:`fill_cell`, :py:meth:`fill_bins`
        """
        i_cell = self.pos_to_cell(x)

        if self.fill_cell(i_cell, False) != i_cell:
            return -1

        for d in range(self.dimension):
            self._sumWeightsX[d] += x[d]
            self._sumWeightsX2[d] += x[d] * x[d]

        return i_cell

    def fill_pos_w(self, x, w: float) -> int:
        """ Fill the histogram with weight.

        Args:
            x (array-like): the position for each dimension. The size of the array is the same as the number of dimensions

            w (float): the weight to fill in

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        NOTE:
            x contains coordinates not indexes of the bins

        See Also:
            :py:meth:`fill_cell_w`, :py:meth:`fill_bins_w`
        """
        i_cell = self.pos_to_cell(x)

        if self.fill_cell_w(i_cell, w, False) != i_cell:
            return -1

        for d in range(self.dimension):
            self._sumWeightsX[d] += w * x[d]
            self._sumWeightsX2[d] += w * x[d] * x[d]

        return i_cell

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

            result.fill_cell_w(i_cell, val1 + val2)

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
            scaledHist._binSumWeightsVals2[i_cell] = factor * scaledHist._binSumWeightsVals2[i_cell]
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

            result.fill_cell_w(i_cell, val1 + val2)

        return result

    def __sub__(self, other):
        """Substract 2 histograms

        Args:
            other (HistND): a histogram of the same dimension.

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

            result.fill_cell_w(i_cell, val1 - val2)

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

            result.fill_cell_w(i_cell, val1 * val2)

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
                result.fill_cell_w(i_cell, 0)
            else:
                result.fill_cell_w(i_cell, val1 / val2)

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
            return 0.0

        if 0 > b or b > self.cells:
            return 0.0

        if a >= b:
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

    def integral_over_bins(self, minBinsIds, maxBinsIds) -> float:
        """ Computes integral over bins range

        Args:
            minBinsIds (array-like): an array of ints containing the minimum bins over each dimension

            maxBinsIds (array-like): an array of ints containing the maximum bins over each dimension

        Returns:
            float.

        See Also:
            :py:meth:`integral`, :py:meth:`integral_over_pos`
        """
        min_cell_id = self.bins_to_cell(minBinsIds)
        max_cell_id = self.bins_to_cell(maxBinsIds)

        return self.integral(min_cell_id, max_cell_id)

    def integral_over_pos(self, minPos, maxPos) -> float:
        """ Computes integral between 2 positions.

        Args:
            minPos (array-like): an array of floats containing the minimum position on each dimension

            maxPos (array-like): an array of floats containing the maximum position on each dimension

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

    def fill(self, x: float) -> int:
        """ Fill the histogram (no weights).

        Args:
            x (float): the coordinates on the axis of a bin.

        NOTE: 
            x is coordinate not index of the bins

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell  was found or the input values are not valid

        See Also:
            :py:meth:`HistND.fill_cell`, :py:meth:`HistND.fill_bins`, :py:meth:`HistND.fill_pos`
        """
        return self.fill_pos([x])

    def fill_w(self, x: float, w: float) -> int:
        """ Fill the histogram with weights.

        Args:
            x (float): the coordinates on the axis of a bin.

            w (float): the weight to fill in

        NOTE: 
            x is coordinate not index of the bins

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        See Also:
            :py:meth:`HistND.fill_cell_w`, :py:meth:`HistND.fill_bins_w`, :py:meth:`HistND.fill_pos_w`
        """
        return self.fill_pos_w([x], w)


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

    def fill(self, x: float, y: float) -> int:
        """ Fill the histogram (no weights).

        Args:
            x (float): the coordinates of a bin on the X-axis.

            y (float): the coordinates of a bin on the Y-axis.

        NOTE: 
            x, y are coordinates not indexes of the bins

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        See Also:
            :py:meth:`HistND.fill_cell`, :py:meth:`HistND.fill_bins`, :py:meth:`HistND.fill_pos`
        """
        return self.fill_pos([x, y])

    def fill_w(self, x: float, y: float, w: float) -> int:
        """ Fill the histogram with weights.

        Args:
            x (float): the coordinates of a bin on the X-axis.

            y (float): the coordinates of a bin on the Y-axis.

            w (float): the weight to fill in

        NOTE: 
            x, y are coordinates not indexes of the bins

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        See Also:
            :py:meth:`HistND.fill_cell_w`, :py:meth:`HistND.fill_bins_w`, :py:meth:`HistND.fill_pos_w`
        """
        return self.fill_pos_w([x, y], w)

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

    def fill(self, x: float, y: float, z: float) -> int:
        """ Fill the histogram (no weights).

        Args:
            x (float): the coordinates of a bin on the X-axis.

            y (float): the coordinates of a bin on the Y-axis.

            z (float): the coordinates of a bin on the Z-axis.

        NOTE: 
            x, y, z are coordinates not indexes of the bins

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        See Also:
            :py:meth:`HistND.fill_cell`, :py:meth:`HistND.fill_bins`, :py:meth:`HistND.fill_pos`
        """
        return self.fill_pos([x, y, z])

    def fill_w(self, x: float, y: float, z: float, w: float) -> int:
        """ Fill the histogram with weights.

        Args:
            x (float): the coordinates of a bin on the X-axis.

            y (float): the coordinates of a bin on the Y-axis.

            z (float): the coordinates of a bin on the Z-axis.

            w (float): the weight to fill in

        NOTE: 
            x, y, z are coordinates not indexes of the bins

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        See Also:
            :py:meth:`HistND.fill_cell_w`, :py:meth:`HistND.fill_bins_w`, :py:meth:`HistND.fill_pos_w`
        """
        return self.fill_pos_w([x, y, z], w)

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
