""" Wire module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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

from typing import Dict, Tuple, List, Callable
import numpy as np
from PyQt5.QtCore import QThread
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Debug import Debug
from magneticalc.Validatable import Validatable, require_valid, validator


class Wire(Validatable):
    """ Wire class. """

    def __init__(self) -> None:
        """
        Initializes an empty wire.
        A 3D piecewise linear curve with some DC current associated with it.
        """
        Validatable.__init__(self)
        Debug(self, ": Init", init=True)

        self.points_base = np.array([])
        self.points_transformed = np.array([])

        """ Bounding box: Minimum bounds (3D point), maximum bounds (3D point). """
        self.bounds = np.array([]), np.array([])

        self._slicer_limit = 0
        self.dc = 0

        self._points_sliced = np.array([])
        self._length = 0

        """ Wire Elements: Ordered list of segment center points and directions. """
        self._elements = np.array([])

    def set(
            self,
            points: np.ndarray,
            stretch: np.ndarray,
            rotational_symmetry: Dict,
            close_loop: bool,
            slicer_limit: float,
            dc: float
    ) -> None:
        """
        Sets the parameters.

        @param points: Ordered list of 3D coordinates (see presets)
        @param stretch: XYZ stretch transform factors (3D point)
        @param rotational_symmetry: Dictionary for rotational symmetry transform
        @param close_loop: Enable to transform the wire into a closed loop (append first point)
        @param slicer_limit: Slicer limit
        @param dc: Wire current (A)
        """
        self._slicer_limit = slicer_limit
        self.dc = dc

        self._points_sliced = np.array([])
        self._length = 0

        self.points_base = np.array(points)

        axes = np.array(points).T
        axes = self._transform_stretch(axes, stretch)
        axes = self._transform_rotational_symmetry(axes, rotational_symmetry, close_loop=close_loop)
        self.points_transformed = axes.T

        self.bounds = [min(axes[0]), min(axes[1]), min(axes[2])], [max(axes[0]), max(axes[1]), max(axes[2])]

        Assert_Dialog(len(self.points_base) >= 2, "Number of points must be >= 2")

    @staticmethod
    def _transform_stretch(axes: np.ndarray, stretch: np.ndarray) -> np.ndarray:
        """
        This transformation stretches (and/or mirrors) this curve by some factor in any direction.
        Use the factor +1 / -1 to retain / mirror the curve in that direction.

        @param axes: Transposed array of Wire points
        @param stretch: XYZ stretch transform factors (3D point)
        @return: Transposed array of Wire points
        """
        for i in range(3):
            axes[i] *= stretch[i]
        return axes

    @staticmethod
    def _transform_rotational_symmetry(axes: np.ndarray, parameters: Dict, close_loop: bool) -> np.ndarray:
        """
        This transformation replicates and rotates this curve `count` times about an `axis` with radius `radius`.

        @param axes: Transposed array of Wire points
        @param parameters: Dictionary containing the transformation parameters
                           (number of replications, radius, axis and offset angle)
        @param close_loop: Enable to transform the wire into a closed loop (append first point)
        @return: Transposed array of Wire points
        """
        x, y, z = [], [], []

        axis_other_1 = (parameters["axis"] + 1) % 3
        axis_other_2 = (parameters["axis"] + 2) % 3

        for a in np.linspace(0, 2 * np.pi, parameters["count"], endpoint=False):
            b = a + parameters["offset"] * np.pi / 180
            x = np.append(x, axes[axis_other_1] * np.sin(b) - (axes[axis_other_2] + parameters["radius"]) * np.cos(b))
            y = np.append(y, axes[axis_other_1] * np.cos(b) + (axes[axis_other_2] + parameters["radius"]) * np.sin(b))
            z = np.append(z, axes[parameters["axis"]])

        axes = [x, y, z]

        if close_loop:
            for i in range(3):
                axes[i] = np.append(axes[i], axes[i][0])

        return np.array(axes)

    # ------------------------------------------------------------------------------------------------------------------

    @validator
    def recalculate(self, progress_callback: Callable) -> bool:
        """
        Slices wire segments into smaller ones until segment lengths equal or undershoot slicer limit.

        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()")

        points_sliced = []
        length = 0

        for i in range(len(self.points_transformed) - 1):

            # Calculate direction and length of wire segment
            segment_direction = np.array(self.points_transformed[i + 1] - self.points_transformed[i])
            segment_length = np.linalg.norm(segment_direction)
            length += segment_length

            # Calculate required number of slices (subdivisions) and perform linear interpolation
            slices = np.ceil(segment_length / self._slicer_limit).astype(int)
            linear = np.linspace(0, 1, slices, endpoint=False)
            points_sliced += [self.points_transformed[i] + segment_direction * j for j in linear]

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(50 * (i + 1) / (len(self.points_transformed) - 1))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): WARNING: Interruption requested, exiting now", warning=True)
                    return False

        # Append the very last point since it is not appended by the interpolation above
        points_sliced.append(self.points_transformed[-1])

        self._points_sliced = np.array(points_sliced)
        self._length = length

        # Calculate wire elements: [[element_center, element_direction], …]
        elements = []
        for i in range(len(self._points_sliced) - 1):

            element_direction = np.array(self._points_sliced[i + 1]) - np.array(self._points_sliced[i])
            element_center = self._points_sliced[i] + element_direction / 2
            elements.append([element_center, element_direction])

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(50 + 50 * (i + 1) / (len(self._points_sliced) - 1))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): WARNING: Interruption requested, exiting now", warning=True)
                    return False

        self._elements = np.array(elements)

        progress_callback(100)

        return True

    @property
    @require_valid
    def points_sliced(self) -> np.ndarray:
        """
        Returns this wire's points after slicing.

        @return: Ordered list of 3D points
        """
        return self._points_sliced

    @property
    @require_valid
    def length(self) -> float:
        """
        @return: Wire length
        """
        return self._length

    @property
    @require_valid
    def elements(self) -> np.ndarray:
        """
        @return: Wire elements
        """
        return self._elements
