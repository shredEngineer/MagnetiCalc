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
from PyQt5.QtCore import *
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Debug import Debug


class SamplingVolume:
    """ Sampling volume class. """

    def __init__(self, resolution):
        """
        Initializes an empty sampling volume, with zero bounds and no constraints.

        @param resolution: Resolution
        """
        Debug(self, ": Init")

        self.resolution = resolution

        self.constraints = []

        self.bounds_min = np.zeros(3)
        self.bounds_max = np.zeros(3)

        self._points = None

        Assert_Dialog(resolution > 0, "Resolution must be > 0")

    def is_valid(self):
        """ Indicates valid data for display. """
        return self._points is not None

    def invalidate(self):
        """ Resets data, hiding from display. """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._points = None

    # ------------------------------------------------------------------------------------------------------------------

    def get_bounds(self):
        """
        Returns this volume's bounding box.

        @return: bounds_min, bounds_max
        """
        return self.bounds_min, self.bounds_max

    def get_points(self):
        """
        Returns this sampling volume's points.

        @return: List of 3D points
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated sampling volume")

        return self._points

    # ------------------------------------------------------------------------------------------------------------------

    def set_bounds_nearest(self, bounds_min, bounds_max):
        """
        Adjusts this volume's bounding box to fully enclose a 3D wire curve.
        This expands the bounding box to the next integer grid coordinates.

        Note: This will not automatically invalidate the sampling volume

        @param bounds_min: Minimum bounding box point
        @param bounds_max: Maximum bounding box point
        @return: Rounded (bounds_min, bounds_max)
        """
        self.bounds_min = np.array([np.floor(x) for x in bounds_min])
        self.bounds_max = np.array([np.ceil(x) for x in bounds_max])

    def set_padding(self, dx, dy, dz):
        """
        Shrinks or enlarges this volume's bounding box by some amount, in each direction, symmetrically.

        Note: This will not automatically invalidate the sampling volume

        @param dx: Amount of padding in X-direction.
        @param dy: Amount of padding in Y-direction.
        @param dz: Amount of padding in Z-direction.
        """
        self.bounds_min = list(np.array(self.bounds_min) - np.array([dx, dy, dz]))
        self.bounds_max = list(np.array(self.bounds_max) + np.array([dx, dy, dz]))

    # ------------------------------------------------------------------------------------------------------------------

    def add_constraint(self, lambda_expression):
        """
        Adds some constraint to this volume's point generator.

        @param lambda_expression: Lambda expression, evaluating to boolean (dict as argument, see L{constraint_dict})
        """
        Debug(self, f".add_constraint()")

        self.constraints.append(lambda_expression)

    @staticmethod
    def constraint_dict(x, y, z):
        """
        Returns a parameters for a given point, containing its coordinates, 3D radius and 2D radii in different planes.

        @param x: X-coordinate
        @param y: Y-coordinate
        @param z: Z-coordinate
        @return: Constraint variables parameters
        """
        return {
            "x": x,
            "y": y,
            "z": z,
            "radius": np.linalg.norm(np.array([x, y, z])),
            "radius_xy": np.linalg.norm(np.array([x, y])),
            "radius_xz": np.linalg.norm(np.array([x, z])),
            "radius_yz": np.linalg.norm(np.array([y, z]))
        }

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self, progress_callback):
        """
        Recalculates the sampling volume points.

        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()", color=(0, 128, 0))

        coordinates = [[], [], []]
        for i in range(3):
            steps = np.ceil((self.bounds_max[i] - self.bounds_min[i]) * self.resolution).astype(int) + 1
            coordinates[i] = np.linspace(self.bounds_min[i], self.bounds_max[i], steps)

        # Calculate total number of possible points
        n = len(coordinates[0]) * len(coordinates[1]) * len(coordinates[2])

        points = []

        # Iterate through all possible points
        x, y, z = 0, 0, 0
        for i in range(n):
            point = np.array([coordinates[0][x], coordinates[1][y], coordinates[2][z]])

            # Linear access
            if x + 1 < len(coordinates[0]):
                x += 1
            else:
                x = 0
                if y + 1 < len(coordinates[1]):
                    y += 1
                else:
                    y = 0
                    z += 1

            # Calculate inclusion relation
            inclusion = True
            for constraint in self.constraints:
                if not constraint(SamplingVolume.constraint_dict(*point)):
                    inclusion = False
                    break
            if inclusion:
                points.append(point)

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(100 * (i + 1) / n)

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): Interruption requested, exiting now", color=(0, 0, 255))
                    return False

        self._points = np.array(points)

        Debug(
            self,
            ".recalculate(): "
            f"Calculated {len(self.constraints)} constraints "
            f"over {n} possible points, "
            f"yielded {len(self._points)} points",
            color=(0, 0, 255)
        )

        return True
