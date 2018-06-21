# -*- coding: utf-8 -*-
"""

Note:
    The classes defined in this module do **NOT** provide drawing capabilities, so there is **NO** draw() nor paint()
    method. Use other libraries like matplotlib to plot the data. But for your convenience, this package provides a 
    module for easy plotting using matplotlib. See, :py:mod:`rootplots.mpl`
"""

import math
import warnings
from typing import List, Sequence

from . import hist as h

__all__ = 'ProfileND', 'Profile1D', 'Profile2D', 'Profile3D'


class ProfileND(h.HistND):
    """ Profile histograms are used to compute the mean value of Y and its error for each bin in X.

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

    """
    _sumWeightedValues: int
    _sumWeightedValues2: int
    _binSumWeightsValues2: List[float]

    def __init__(self, dim: int, minBin: Sequence, maxBin: Sequence, nBins: Sequence, minValue: float=None,
                 maxValue: float=None, title=str()):
        h.HistND.__init__(self, dim, minBin, maxBin, nBins, title)

        self._minValue = minValue
        self._maxValue = maxValue

        ############################################
        # Values computed during each fill

        # some stats
        self._sumWeightedValues = 0  # Total Sum of weight*Y
        self._sumWeightedValues2 = 0  # Total Sum of weight*Y*Y

        self._binsValues = []  # contains the values per cell (global linear bin)
        self._binSumWeightsValues2 = []  # array of sum of weighted squared values per cell

        for v in range(self.cells):
            self._binsValues.append(0)
            self._binSumWeightsValues2.append(0)

    @property
    def minY(self):
        return self._minValue

    @property
    def maxY(self):
        return self._maxValue

    def _get_std_deviation(self, j: int):
        H = self._binsValues[j]
        L = self._binsEntries[j]
        E = self._binSumWeightsValues2[j]
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

    def fill_cell(self, i_cell: int, value: float = None, weight: float = 1.0, error_per_bin=True) -> int:
        """ Fill the profile using global cell index.

        Args:
            i_cell (int): the global bin index (cell index).

            weight (float): the weight to fill in. Defaults to 1.0

            value (float): a value to fill in the cell. This argument must not be None.

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
        if value is None:
            raise ValueError("Argument 'value' can not be None")

        if self._minValue is not None and value < self._minValue:  # ignore filtered data
            return -1
        if self._maxValue is not None and value > self._maxValue:  # ignore filtered data
            return -1

        i_cell = super(ProfileND, self).fill_cell(i_cell, value=value, weight=weight, error_per_bin=error_per_bin)
        if i_cell >= 0:
            self._binsValues[i_cell] += weight * value
            self._binSumWeightsValues2[i_cell] += weight * value * value
            self._sumWeightedValues += weight * value
            self._sumWeightedValues2 += weight * value * value
        return i_cell

    def fill_bins(self, arr: Sequence, value: float=None, weight: float=1.0) -> int:
        """ Fill the histogram using bin indexes.

        Args:
            arr (Sequence): the bin indexes for each dimension. The size of the array is the same as the number of dimensions

            weight (float): the weight to fill in

            value (float): a value to fill in the cell. This argument must not be None.

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values are not valid

        NOTE:
            arr contains indexes of the bins on each axis, not the positions on axis

        See Also:
            :py:meth:`fill_pos`, :py:meth:`fill_cell`
        """
        if value is None:
            raise ValueError("Argument 'value' can not be None")

        if self._minValue is not None and value < self._minValue:  # ignore filtered data
            return -1
        if self._maxValue is not None and value > self._maxValue:  # ignore filtered data
            return -1

        i_cell = super(ProfileND, self).fill_bins(arr, value=value, weight=weight)
        if i_cell >= 0:
            self._binsValues[i_cell] += weight * value
            self._binSumWeightsValues2[i_cell] += weight * value * value
            self._sumWeightedValues += weight * value
            self._sumWeightedValues2 += weight * value * value
        return i_cell

    def fill_pos(self, x: Sequence, value: float=None, weight: float=1.0) -> int:
        """ Fill the profile using a position.

        Args:
            x (Sequence): the coordinates on the axis of a cell. The size of the array is the same as the number of dimensions

            weight (float): the weight to fill in. Defaults to 1.0

            value (float): a value to fill in the cell. This argument must not be None.

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
        are not valid

        NOTE:
            x contains coordinates not indexes of the bins

        See Also:
            :py:meth:`fill_cell`, :py:meth:`fill_bins`
        """
        if value is None:
            raise ValueError("Argument 'value' can not be None")

        if self._minValue is not None and value < self._minValue:  # ignore filtered data
            return -1
        if self._maxValue is not None and value > self._maxValue:  # ignore filtered data
            return -1

        i_cell = super(ProfileND, self).fill_pos(x, value, weight=weight)
        if i_cell >= 0:
            self._binsValues[i_cell] += weight * value
            self._binSumWeightsValues2[i_cell] += weight * value * value
            self._sumWeightedValues += weight * value
            self._sumWeightedValues2 += weight * value * value
        return i_cell

    def fill(self, x: float = None, y: float = None, z: float = None, arr: Sequence = None, value: float = None,
             weight: float = 1.0) -> int:
        """ Fill the profile (using coordinate positions). Use this and not other fill*() methods of the parent histogram.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D profiles.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D profiles.

            z (float): the coordinate on the third axis of the histogram. Used only 3D profiles.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
            If using arr the function will ignore the arguments x,y,z. This argument is used when having
            profiles higher then 3D. Its length **must be** the same as the profiles dimension.

            value (float): a value to fill in the cell. This argument must not be None.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected bin or -1** if no bin
            was found or the input values are not valid
        """
        if value is None:
            raise ValueError("Argument 'value' can not be None")

        if self._minValue is not None and value < self._minValue:  # ignore filtered data
            return -1
        if self._maxValue is not None and value > self._maxValue:  # ignore filtered data
            return -1

        i_cell = super(ProfileND, self).fill(x, y, z, arr, value, weight)
        if i_cell >= 0:
            self._binsValues[i_cell] += weight * value
            self._binSumWeightsValues2[i_cell] += weight * value * value
            self._sumWeightedValues += weight * value
            self._sumWeightedValues2 += weight * value * value
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

    def fill(self, x: float=None, y: float=None, z: float=None, arr: Sequence=None, value: float=None,
             weight: float=1.0) -> int:
        """ Fill the profile.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D profiles.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D profiles.

            z (float): the coordinate on the third axis of the histogram. Used only 3D profiles.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
            If using arr the function will ignore the arguments x,y,z. This argument is used when having
            histograms higher then 3D. Its length **must be** the same as the profile dimension, it is not checked.

            value (float): a value to fill in the cell. This argument must not be None.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
        are not valid
        """
        if arr is not None:
            return super(Profile1D, self).fill(arr=arr, value=value, weight=weight)

        # arr is None
        if x is None:
            raise ValueError("Argument x cannot be None")

        if y is not None or z is not None:
            warnings.warn("Second and third arguments are not supported for 1D profiles. Ignoring arguments y and z..")

        return super(Profile1D, self).fill(x, value=value, weight=weight)


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

    def fill(self, x: float=None, y: float=None, z: float=None, arr: Sequence=None, value: float=None,
             weight: float=1.0) -> int:
        """ Fill the profile.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D profiles.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D profiles.

            z (float): the coordinate on the third axis of the histogram. Used only 3D profiles.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
            If using arr the function will ignore the arguments x,y,z. This argument is used when having
            histograms higher then 3D. Its length **must be** the same as the profile dimension, it is not checked.

            value (float): a value to fill in the cell. This argument must not be None.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
        are not valid
        """
        if arr is not None:
            return super(Profile2D, self).fill(arr=arr, value=value, weight=weight)

        # arr is None
        if x is None:
            raise ValueError("Argument x cannot be None")

        if y is None:
            raise ValueError("Argument y cannot be None")

        if z is not None:
            warnings.warn("Third argument is not supported for 2D profiles. Ignoring argument 'z'..")

        return super(Profile2D, self).fill(x, y, value=value, weight=weight)


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

    def fill(self, x: float=None, y: float=None, z: float=None, arr: Sequence=None, value: float=None,
             weight: float=1.0) -> int:
        """ Fill the profile.

        Args:
            x (float): the coordinate on the first axis of the histogram. Used by 1D, 2D and 3D profiles.

            y (float): the coordinate on the second axis of the histogram. Used by 2D and 3D profiles.

            z (float): the coordinate on the third axis of the histogram. Used only 3D profiles.

            arr (Sequence): an Sequence sequence of floats representing the N-dimensional coordinates of a point.
            If using arr the function will ignore the arguments x,y,z. This argument is used when having
            histograms higher then 3D. Its length **must be** the same as the profile dimension, it is not checked.

            value (float): a value to fill in the cell. This argument must not be None.

            weight (float): the weight to fill in. Defaults to 1.0

        Returns:
            int. The **index of the affected cell (global linear bin) or -1** if no cell was found or the input values
        are not valid
        """
        if arr is not None:
            return super(Profile3D, self).fill(arr=arr, value=value, weight=weight)

        # arr is None
        if x is None:
            raise ValueError("Argument x cannot be None")

        if y is None:
            raise ValueError("Argument y cannot be None")

        if z is None:
            raise ValueError("Argument z cannot be None")

        return super(Profile3D, self).fill(x, y, z, value=value, weight=weight)
