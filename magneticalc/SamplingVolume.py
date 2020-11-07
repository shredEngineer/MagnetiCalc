""" Sampling volume module. """

#  ISC License
#
#  Copyright (c) 2020, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import numpy as np
from PyQt5.QtCore import QThread
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


class SamplingVolume:
    """ Sampling volume class. """

    def __init__(self, resolution: int):
        """
        Initializes an empty sampling volume, with zero bounds and no constraints.

        @param resolution: Resolution
        """
        Debug(self, ": Init")

        self._resolution = resolution

        self.constraints = []

        self._bounds_min = np.zeros(3)
        self._bounds_max = np.zeros(3)

        self._points = None
        self._labeled_indices = None

        Assert_Dialog(resolution > 0, "Resolution must be > 0")

    def is_valid(self):
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self._points is not None and \
            self._labeled_indices is not None

    def invalidate(self):
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._points = None
        self._labeled_indices = None

    # ------------------------------------------------------------------------------------------------------------------

    def get_resolution(self):
        """
        Returns this volume's resolution.

        @return: Resolution
        """
        return self._resolution

    def get_bounds(self):
        """
        Returns this volume's bounding box.

        @return: _bounds_min, _bounds_max
        """
        return self._bounds_min, self._bounds_max

    def get_points(self):
        """
        Returns this sampling volume's points.

        @return: Ordered list of 3D points
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated sampling volume")

        return self._points

    def get_labeled_indices(self):
        """
        Returns this sampling volume's labeled indices; an unordered list of tuples (sampling volume point, field index)

        @return: Labeled indices
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated sampling volume")

        return self._labeled_indices

    # ------------------------------------------------------------------------------------------------------------------

    def set_bounds_nearest(self, bounds_min, bounds_max):
        """
        Adjusts this volume's bounding box to fully enclose a 3D wire curve.
        This expands the bounding box to the next integer grid coordinates.

        Note: This will not automatically invalidate the sampling volume

        @param bounds_min: Minimum bounding box point
        @param bounds_max: Maximum bounding box point
        @return: Rounded (_bounds_min, _bounds_max)
        """
        self._bounds_min = np.array([np.floor(x) for x in bounds_min])
        self._bounds_max = np.array([np.ceil(x) for x in bounds_max])

    def set_padding_nearest(self, padding):
        """
        Shrinks or enlarges this volume's bounding box by some amount, in each direction, symmetrically.
        This expands the bounding box to the next integer grid coordinates.

        Note: This will not automatically invalidate the sampling volume

        @param padding: Amount of padding (3D point)
        """
        self._bounds_min -= np.array([np.floor(x) for x in padding])
        self._bounds_max += np.array([np.ceil(x) for x in padding])

    # ------------------------------------------------------------------------------------------------------------------

    def add_constraint(self, constraint):
        """
        Adds some constraint to this volume's point generator.

        @param constraint: Constraint
        """
        Debug(self, f".add_constraint()")

        self.constraints.append(constraint)

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self, progress_callback):
        """
        Recalculates the sampling volume points.

        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()", color=(0, 128, 0))

        # Calculate all possible grid points
        points_axes_all = [[], [], []]
        for i in range(3):
            steps = np.ceil((self._bounds_max[i] - self._bounds_min[i]) * self._resolution).astype(int) + 1
            points_axes_all[i] = np.linspace(self._bounds_min[i], self._bounds_max[i], steps)

        points_included = []
        labeled_indices = []

        # Linearly iterate through all possible grid points, computing the 3D cartesian ("euclidean") product
        span = np.array([len(axis) for axis in points_axes_all])
        n = span[0] * span[1] * span[2]
        x, y, z = 0, 0, 0
        for i in range(n):

            point = np.array([points_axes_all[0][x], points_axes_all[1][y], points_axes_all[2][z]])

            # Calculate the inclusion relation
            inclusion = True
            for constraint in self.constraints:
                if not constraint.evaluate(point):
                    inclusion = False
                    break  # AND-behaviour

            if inclusion:
                # Include point
                points_included.append(point)

                # Provide 1 cm of orthogonal spacing between labels
                if x % self._resolution == 0 and y % self._resolution == 0 and z % self._resolution == 0:
                    labeled_index = (point, len(points_included) - 1)
                    labeled_indices.append(labeled_index)

            # Move to the next grid point
            if x + 1 < span[0]:
                x += 1
            else:
                x = 0
                if y + 1 < span[1]:
                    y += 1
                else:
                    y = 0
                    z += 1

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(100 * (i + 1) / n)

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): Interruption requested, exiting now", color=Theme.PrimaryColor)
                    return False

        self._points = np.array(points_included)
        self._labeled_indices = labeled_indices

        Debug(
            self,
            ".recalculate(): "
            f"Calculated {len(self.constraints)} constraints "
            f"over {n} possible points, "
            f"yielded {len(self._points)} points",
            color=Theme.PrimaryColor
        )

        return True
