# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 11:51:31 2018

@author: Mihai Niculescu <mihai@spacescience.ro>
"""

import math
from typing import List

from . import hist as h

__all__ = 'ProfileND, Profile1D, Profile2D, Profile3D'


class ProfileND(h.HistND):
    """ Profile histograms are used to compute the mean value of Y and its error for each bin in X.

    This class does not provide drawing posibilities, so there is no draw() method. Use other libraries,like matplotlib,
    to rootplots the data, see example below.

    For each bin we have::

    - The mean of Y is the sum of all values in that bin divided by the number of entries per bin.
    - The error on X is the width of the bin divided by 2.
    - The error on Y is the standard deviation divided by the sqrt(number_of_entries_per_bin).

    Args:
        dim (int):  the number of dimensions of the profile

        minBin (array like): an array containing the minimum value of lower edge of bins for each dimension.

        maxBin (array like): an array containing the maximum value of upper edge of bins for each dimension.

        nBins (array like):  an array containing the number of bins for each dimension.

        title (string): the title of the profile.

        minValue (float): the minimum value accepted to fill a bin.
            the lowest value accepted on Y (vertical axis).
            This filter is not used when minValue is None

        maxValue (float): the maximum value accepted to fill a bin.
            the highest value accepted on Y (vertical axis).
            This filter is not used when maxValue is None

    A simple profile bins start from `0.1` to `5.1` and contains `10 bins`, without limits on Y

    >>> prof = ProfileND(1, [0.1], [5.1], [10])

    If you want limits on Y, let say discard those values that are not within
    [-1,1] use as

    >>> prof = ProfileND(1, [0.1], [5.1], [10], -1, 1)

    Fill the profilehist

    >>> prof.fill([2.3], 10.)

    Full example::

        import rootplots.profile as pr
        import rootplots.mpl as mpl
        import random

        hprof = pr.ProfileND(1, [-4],[4], [100], 0, 20)
        for i in range(2500):
            px = random.gauss(0,1)
            py = random.gauss(0,1)
            pz = px*px + py*py

            hprof.fill([px],pz)

        mpl.plot_profile(hprof)
        mpl.show()
    """
    def __init__(self, dim: int, minBin, maxBin, nBins, minValue=None, maxValue=None, title=str()):
        h.HistND.__init__(self, dim, minBin, maxBin, nBins, title)

        self._minValue = minValue
        self._maxValue = maxValue

        ############################################
        # Values computed during each fill

        # some stats
        self._sumWeightedVals = 0  # Total Sum of weight*Y
        self._sumWeightedVals2 = 0  # Total Sum of weight*Y*Y

        self._binsValues = []  # contains the values per cell (global linear bin)
        self._binSumWeightsVals2 = []  # array of sum of weighted squared values per cell

        for v in range(self.cells):
            self._binsValues.append(0)
            self._binSumWeightsVals2.append(0)

    @property
    def minY(self):
        return self._minValue

    @property
    def maxY(self):
        return self._maxValue

    def _get_std_deviation(self, j):
        H = self._binsValues[j]
        L = self._binsEntries[j]
        E = self._binSumWeightsVals2[j]
        return math.sqrt(E * L - H * H)/L  # std deviation = sqrt(rms**2 - mean**2)

    def get_cell_content(self, i: int) -> float:
        """ Returns the content of the cell 'i'

        Args:
            i (int): a valid cell index (aka global linear bin)

        Returns:
            float or 0.0 if the position is outside cells ranges
        """
        n = h.HistND.get_cell_content(self, i)
        if n == 0.0:
            return 0.0
        else:
            return self._binsValues[i] / n

    def get_cells_contents(self, includeEmptyBins=False) -> List[float]:
        """ Returns the contents of all bins (cells) per each dimension.
        By default it **does not** include empty cells.

       Args:
           includeEmptyBins (bool): if empty bins are included in the list.
               If True then empty bins are included, otherwise they are NOT included

       Returns:
           list of list.
       """
        result = []
        for i_cell in range(self.cells):
            L = self._binsEntries[i_cell]
            if L == 0:
                if includeEmptyBins:
                    result.append(0)
                else:
                    continue
            else:
                result.append(self._binsValues[i_cell] / L)
        return result

    def get_cell_content_error(self, i: int) -> float:
        """Returns the error value associated with cell 'i'

        The error on per cell is the standard deviation (in that cell) divided by the sqrt(number_of_entries_per_cell).

        Args:
            i (int): a valid cell index (aka global linear bin)

        Returns:
            float.
        """
        L = self._binsEntries[i]
        if L == 0:
            return 0.0
        else:
            return self._get_std_deviation(i) / math.sqrt(self._binsEntries[i])

    def get_cells_contents_errors(self, includeEmptyBins=False) -> List[float]:
        """ Returns a list containing the errors on the Y axis associated to each bin.
        By default it **does not** include empty bins.

        The error on Y per bin is the standard deviation (in that bin) divided by the sqrt(number_of_entries_per_bin).

        Args:
            includeEmptyBins (bool): if empty bins are included in the list.
                If True then empty bins are included, otherwise they are NOT included

        Returns:
            list.
        """
        result = []
        for iBin in range(self.cells):
            L = self._binsEntries[iBin]
            if L == 0:
                if includeEmptyBins:
                    result.append(0)
                else:
                    continue
            else:
                result.append(self._get_std_deviation(iBin) / math.sqrt(self._binsEntries[iBin]))
        return result

    def fill_profile(self, x, val: float) -> int:
        """ Fill the profile (without weights). Use this and not the fill*() methods of the parent histogram.

        Args:
            x (array-like): the coordinates on the axis of a cell.
            The size of the array is the same as the number of dimensions

            NOTE - x contains coordinates not indexes of the bins

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.

        Returns:
            int. The **index of the affected bin or -1** if no bin
            was found or the input values are not valid
        """
        if val is None:
            return -1

        if self._minValue is not None and val < self._minValue:
            return -1
        if self._maxValue is not None and val > self._maxValue:
            return -1

        i_cell = h.HistND.fill_pos(self, x)
        if i_cell >= 0:
            self._binsValues[i_cell] += val
            self._binSumWeightsVals2[i_cell] += val * val
            self._sumWeightedVals += val
            self._sumWeightedVals2 += val * val
        return i_cell

    def fill_profile_w(self, x, val: float, w: float=1) -> int:
        """ Fill the profile with weights. Use this and not the fill*() methods of the parent histogram.

        Args:
            x (array-like): the coordinates on the axis of a cell.
            The size of the array is the same as the number of dimensions

            NOTE - x contains coordinates not indexes of the bins

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.


            w (float): a weight associated with Y value

        Returns:
            int. The **index of the affected bin or 0** if no bin
            was found or the input values are not valid
        """
        if self._minValue is not None and val < self._minValue:
            return 0
        if self._maxValue is not None and val > self._maxValue:
            return 0

        i_cell = h.HistND.fill_pos_w(self, x, w)
        if i_cell >= 0:
            self._binsValues[i_cell] += w * val
            self._binSumWeightsVals2[i_cell] += w * val * val
            self._sumWeightedVals += w * val
            self._sumWeightedVals2 += w * val * val
        return i_cell


class Profile1D(ProfileND):
    """ A 1-Dimensional Profile

    Args:
        minBin (float): the minimum value of lower edge of bins

        maxBin (float): the maximum value of upper edge of bins

        nBins (integer): the number of bins

        title (string): the title of the histogram
    """
    def __init__(self, nBins: int, minBin: float, maxBin: float, minValue=None, maxValue=None, title=str()):
        ProfileND.__init__(self, 1, [minBin], [maxBin], [nBins], minValue, maxValue, title)

    def fill(self, x: float, val: float) -> int:
        """ Fill the histogram (no weights).

        Args:
            x (float): the coordinates on the X-axis of a bin.

            NOTE - x contains coordinates not indexes of the bins

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.

        Returns:
            int. The **index of the affected bin or -1** if no bin
            was found or the input values are not valid
        """
        return ProfileND.fill_profile(self, [x], val)

    def fill_w(self, x: float, val: float, w: float=1) -> int:
        """ Fill the histogram with weights.

        Args:
            x (float): the coordinates on the X-axis of a bin.

            NOTE - x contains coordinates not indexes of the bins

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.

            w (float): a weight associated with Y value

        Returns:
            int. The **index of the affected bin or 0** if no bin
            was found or the input values are not valid
        """
        return ProfileND.fill_profile_w(self, [x], val, w)


class Profile2D(ProfileND):
    """ A 2-Dimensional Profile

     Args:
        nBinsX (integer): the number of bins on the X-axis

        minBinX (float): the minimum value of lower edge of bins on the X-axis

        maxBinX (float): the maximum value of upper edge of bins on the X-axis

        nBinsY (integer): the number of bins on the Y-axis

        minBinY (float): the minimum value of lower edge of bins on the Y-axis

        maxBinY (float): the maximum value of upper edge of bins on the Y-axis

        title (string): the title of the histogram
    """
    def __init__(self, nBinsX: int, minBinX: float, maxBinX: float, nBinsY: int, minBinY: float, maxBinY: float,
                 minValue=None, maxValue=None, title=str()):
        ProfileND.__init__(self, 2, [minBinX, minBinY], [maxBinX, maxBinY], [nBinsX, nBinsY], minValue, maxValue, title)

    def fill(self, x: float, y: float, val: float) -> int:
        """ Fill the histogram (no weights).

        Args:
            x (float): the coordinates on the X-axis of a bin.

            y (float): the coordinates on the Y-axis of a bin.

            NOTE - x, y are coordinates inside a valid bin and not bin indexes

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.

        Returns:
            int. The **index of the affected bin or -1** if no bin
            was found or the input values are not valid
        """
        return ProfileND.fill_profile(self, [x, y], val)

    def fill_w(self, x: float, y: float, val: float, w: float=1) -> int:
        """ Fill the histogram with weights.

        Args:
            x (float): the coordinates on the X-axis of a bin.

            y (float): the coordinates on the Y-axis of a bin.

            NOTE - x, y are coordinates inside a valid bin and not bin indexes

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.

            w (float): a weight associated with Y value

        Returns:
            int. The **index of the affected bin or 0** if no bin
            was found or the input values are not valid
        """
        return ProfileND.fill_profile_w(self, [x, y], val, w)


class Profile3D(ProfileND):
    """ A 3-Dimensional Profile

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
    def __init__(self, nBinsX: int, minBinX: float, maxBinX: float, nBinsY: int, minBinY: float, maxBinY: float,
                 nBinsZ: int, minBinZ: float, maxBinZ: float, minValue=None, maxValue=None, title=str()):
        ProfileND.__init__(self, 3, [minBinX, minBinY, minBinZ], [maxBinX, maxBinY, maxBinZ], [nBinsX, nBinsY, nBinsZ],
                           minValue, maxValue, title)

    def fill(self, x: float, y: float, z: float, val: float) -> int:
        """ Fill the histogram (no weights).

        Args:
            x (float): the coordinates on the X-axis of a bin.

            y (float): the coordinates on the Y-axis of a bin.

            z (float): the coordinates on the Z-axis of a bin.

            NOTE - x, y, z are coordinates inside a valid bin and not bin indexes

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.

        Returns:
            int. The **index of the affected bin or -1** if no bin
            was found or the input values are not valid
        """
        return ProfileND.fill_profile(self, [x, y, z], val)

    def fill_w(self, x: float, y: float, z: float, val: float, w: float=1) -> int:
        """ Fill the histogram with weights.

        Args:
            x (float): the coordinates on the X-axis of a bin.

            y (float): the coordinates on the Y-axis of a bin.

            z (float): the coordinates on the Z-axis of a bin.

            NOTE - x, y, z are coordinates inside a valid bin and not bin indexes

            val (float):  a value in that global bin.
                If minValue or maxValue are set (different than None) then `val` is checked
                if its valid: `minValue <= val` or `val <= maxValue`.

            w (float): a weight associated with Y value

        Returns:
            int. The **index of the affected bin or 0** if no bin
            was found or the input values are not valid
        """
        return ProfileND.fill_profile_w(self, [x, y, z], val, w)
