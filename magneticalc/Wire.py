""" Wire module. """

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


class Wire:
    """ Wire class. """

    def __init__(self, points, stretch, rotational_symmetry, slicer_limit: float, dc: float):
        """
        A 3D piecewise linear curve with some DC current associated with it.

        @param points: Ordered list of 3D coordinates (see presets)
        @param stretch: XYZ stretch transform factors (3D point)
        @param rotational_symmetry: Dictionary for rotational symmetry transform
        @param slicer_limit: Slicer limit
        @param dc: Wire current (A)
        """
        Debug(self, ": Init")

        self._points_base = np.array(points)

        # Note: This is my playground for creating new wire presets!
        override_base = False
        if override_base:
            self._points_base = np.array(
                [
                    [
                        i / 128 - 1.125,
                        -np.cos(+2 * np.pi * i / 16) / 2,
                        +np.sin(+2 * np.pi * i / 16) / 2
                    ]
                    for i in range(128)
                ] +
                [
                    [
                        i / 128 + 0.125,
                        -np.cos(-2 * np.pi * (i + 1) / 16) / 2,
                        +np.sin(-2 * np.pi * (i + 1) / 16) / 2
                    ]
                    for i in range(128)
                ]
            )

        self._slicer_limit = slicer_limit
        self._dc = dc

        self._points_sliced = None
        self._length = None

        self._points_transformed = self._points_base.copy()

        self._set_stretch(stretch)
        self._set_rotational_symmetry(rotational_symmetry)

        Assert_Dialog(len(self._points_base) >= 2, "Number of points must be >= 2")

    def is_valid(self):
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self._points_sliced is not None and \
            self._length is not None

    def invalidate(self):
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._points_sliced = None
        self._length = None

    # ------------------------------------------------------------------------------------------------------------------

    def get_bounds(self):
        """
        Returns this curve's bounding box.

        @return: Minimum bounds (3D point), maximum bounds (3D point)
        """
        axes = self.get_points_transformed().transpose()
        bounds_min = [min(axes[0]), min(axes[1]), min(axes[2])]
        bounds_max = [max(axes[0]), max(axes[1]), max(axes[2])]
        return bounds_min, bounds_max

    def get_points_base(self):
        """
        Returns this wire's base points.

        @return: Ordered list of 3D points
        """
        return self._points_base

    def get_points_transformed(self):
        """
        Returns this wire's transformed points.

        @return: Ordered list of 3D points
        """
        return self._points_transformed

    def get_points_sliced(self):
        """
        Returns this wire's points after slicing.

        @return: Ordered list of 3D points
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated wire")

        return self._points_sliced

    def get_elements(self):
        """
        Returns this curve's elements, i.e. an ordered list of segment center points and directions.

        @return: [[element_center, element_direction], ...]
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated wire")

        result = []

        for i in range(len(self._points_sliced) - 1):
            element_direction = np.array(self._points_sliced[i + 1]) - np.array(self._points_sliced[i])
            element_center = self._points_sliced[i] + element_direction / 2
            result.append([element_center, element_direction])

        return np.array(result)

    def get_dc(self) -> float:
        """
        Returns wire current (A).

        @return: Wire current (A)
        """
        return self._dc

    def get_length(self) -> float:
        """
        Returns this curve's length.

        @return: Length
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated wire")

        return self._length

    # ------------------------------------------------------------------------------------------------------------------

    def _set_stretch(self, stretch):
        """
        This transformation stretches (and/or mirrors) this curve by some factor in any direction.
        Use the factor +1 / -1 to retain / mirror the curve in that direction.

        Note: Intended to be called from the class constructor (doesn't automatically invalidate the wire)

        @param stretch: XYZ stretch transform factors (3D point)
        """
        Debug(self, ".stretch()")

        axes = self.get_points_transformed().transpose()

        for i in range(3):
            axes[i] *= stretch[i]

        self._points_transformed = axes.transpose()

    def _set_rotational_symmetry(self, parameters):
        """
        This transformation replicates and rotates this curve `count` times about an `axis` with radius `radius`.

        Note: Intended to be called from the class constructor (doesn't automatically invalidate the wire)

        @param parameters:  Dictionary containing the transformation parameters
                            (number of replications, radius, axis and offset angle)
        """
        Debug(self, "._set_rotational_symmetry()")

        axes = self.get_points_transformed().transpose()

        x, y, z = [], [], []

        axis_other_1 = (parameters["axis"] + 1) % 3
        axis_other_2 = (parameters["axis"] + 2) % 3

        for a in np.linspace(0, 2 * np.pi, parameters["count"], endpoint=False):
            b = a + parameters["offset"] * np.pi / 180
            x = np.append(x, axes[axis_other_1] * np.sin(b) - (axes[axis_other_2] + parameters["radius"]) * np.cos(b))
            y = np.append(y, axes[axis_other_1] * np.cos(b) + (axes[axis_other_2] + parameters["radius"]) * np.sin(b))
            z = np.append(z, axes[parameters["axis"]])

        axes = [x, y, z]

        # Close the resulting loop
        for i in range(3):
            axes[i] = np.append(axes[i], axes[i][0])

        self._points_transformed = np.array(axes).transpose()

        return self

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self, progress_callback) -> bool:
        """
        Slices wire segments into smaller ones until segment lengths equal or undershoot slicer limit.

        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()", color=Theme.SuccessColor)

        points_sliced = []
        length = 0

        for i in range(len(self.get_points_transformed()) - 1):

            # Calculate direction and length of wire segment
            segment_direction = np.array(self.get_points_transformed()[i + 1] - self.get_points_transformed()[i])
            segment_length = np.linalg.norm(segment_direction)
            length += segment_length

            # Calculate required number of slices (subdivisions) and perform linear interpolation
            slices = np.ceil(segment_length / self._slicer_limit).astype(int)
            linear = np.linspace(0, 1, slices, endpoint=False)
            points_sliced += [self.get_points_transformed()[i] + segment_direction * j for j in linear]

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(100 * (i + 1) / (len(self.get_points_transformed()) - 1))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): Interruption requested, exiting now", color=Theme.PrimaryColor)
                    return False

        # Close the loop
        points_sliced.append(self.get_points_transformed()[-1])

        self._points_sliced = np.array(points_sliced)
        self._length = length

        progress_callback(100)

        return True
