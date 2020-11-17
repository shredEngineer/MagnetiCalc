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

    # Enable to show additional debug info during constraint calculation
    Debug_Constraints = False

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
        self._permeabilities = None
        self._labeled_indices = None
        self._neighbor_indices = None

        Assert_Dialog(resolution > 0, "Resolution must be > 0")

    def is_valid(self) -> bool:
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self._points is not None and \
            self._permeabilities is not None and \
            self._labeled_indices is not None and \
            self._neighbor_indices is not None

    def invalidate(self):
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._points = None
        self._permeabilities = None
        self._labeled_indices = None
        self._neighbor_indices = None

    # ------------------------------------------------------------------------------------------------------------------

    def get_resolution(self) -> int:
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

    def get_permeabilities(self):
        """
        Returns this sampling volume's relative permeabilities µ_r.

        @return: Ordered list of sampling volume's relative permeabilities µ_r
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated sampling volume")

        return self._permeabilities

    def get_labeled_indices(self):
        """
        Returns this sampling volume's labeled indices.

        @return: Unordered list of pairs [sampling volume point, field index]
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated sampling volume")

        return self._labeled_indices

    def get_neighbor_indices(self):
        """
        Returns this sampling volume's neighborhood indices.

        @return: Ordered list of sampling volume neighborhood indices (six 3D vectors)
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated sampling volume")

        return self._neighbor_indices

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
        This shrinks or expands the bounding box to the next integer grid coordinates.

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

    def recalculate(self, label_resolution: int, progress_callback) -> bool:
        """
        Recalculates the sampling volume points, permeabilities, labels and neighborhoods according to the constraints.

        @param label_resolution: Label resolution
        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()", color=Theme.SuccessColor)

        # Group constraints by permeability
        constraints_precedence_dict = {}
        for constraint in self.constraints:
            if constraint.permeability in constraints_precedence_dict:
                constraints_precedence_dict[constraint.permeability].append(constraint)
            else:
                constraints_precedence_dict[constraint.permeability] = [constraint]

        if self.Debug_Constraints:
            Debug(
                self,
                f".recalculate(): Created {len(constraints_precedence_dict)} constraint group(s)",
                color=Theme.PrimaryColor,
                force=True
            )

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Calculate all possible grid points
        points_axes_all = [[], [], []]
        for i in range(3):
            steps = np.ceil((self._bounds_max[i] - self._bounds_min[i]) * self._resolution).astype(int) + 1
            points_axes_all[i] = np.linspace(self._bounds_min[i], self._bounds_max[i], steps)

        span = np.array([len(axis) for axis in points_axes_all])
        n = span[0] * span[1] * span[2]

        points_all = np.zeros(shape=(n, 3))
        permeabilities_all = np.zeros(n)
        neighbor_indices_all = [[0, 0, 0, 0, 0, 0]] * n

        labeled_indices = []

        def i_to_xyz(_i: int):
            """
            Convert 1D index to 3D indices.

            @param _i: 1D index
            @return: 3D indices
            """
            _x = _i % span[0]
            _y = (_i // span[0]) % span[1]
            _z = _i // (span[0] * span[1])
            return [_x, _y, _z]

        def xyz_to_i(xyz) -> int:
            """
            Convert 3D indices to 1D index.

            @param xyz: 3D indices
            @return: 1D index
            """
            return xyz[0] + xyz[1] * span[0] + xyz[2] * span[0] * span[1]

        # Linearly iterate through all possible grid points, computing the 3D cartesian ("euclidean") product
        for i in range(n):

            x, y, z = i_to_xyz(i)

            point = np.array([points_axes_all[0][x], points_axes_all[1][y], points_axes_all[2][z]])

            permeability = 1.0  # Default relative permeability for unconstrained points

            # Iterate over constraint groups of descending permeability; higher permeabilities take precedence
            for permeability_key in sorted(constraints_precedence_dict, reverse=True):

                included = True

                if self.Debug_Constraints:
                    print()
                    Debug(
                        self,
                        f".recalculate(): Point = {point}: "
                        f"Calculating {len(constraints_precedence_dict[permeability_key])} constraint(s) "
                        f"for permeability = {permeability_key} …",
                        color=Theme.PrimaryColor,
                        force=True
                    )

                # Calculate the inclusion relation for the current group
                for constraint in constraints_precedence_dict[permeability_key]:

                    if not constraint.evaluate(point):

                        if self.Debug_Constraints:
                            Debug(
                                self,
                                f".recalculate(): Point = {point}: Constraint evaluated to False (breaking)",
                                color=Theme.WarningColor,
                                force=True
                            )

                        # Exclude this point within the current group
                        included = False
                        break

                    else:

                        if self.Debug_Constraints:
                            Debug(
                                self,
                                f".recalculate(): Point = {point}: Constraint evaluated to True",
                                color=Theme.SuccessColor,
                                force=True
                            )

                if included:

                    if self.Debug_Constraints:
                        Debug(
                            self,
                            f".recalculate(): Point = {point}: Included by precedence grouping",
                            color=Theme.SuccessColor,
                            force=True
                        )

                    permeability = permeability_key
                    break

                else:

                    if self.Debug_Constraints:
                        Debug(
                            self,
                            f".recalculate(): Point = {point}: Excluded by precedence grouping",
                            color=Theme.WarningColor,
                            force=True
                        )

            if permeability != 0:

                if self.Debug_Constraints:
                    Debug(
                        self,
                        f".recalculate(): Point = {point}: Finally included with permeability = {permeability}",
                        color=Theme.SuccessColor,
                        force=True
                    )

                # Include this point
                points_all[i] = point
                permeabilities_all[i] = permeability

                # Generate this sampling volume point's neighborhood
                neighborhood = [
                    xyz_to_i([x + 1, y, z]),
                    xyz_to_i([x, y + 1, z]),
                    xyz_to_i([x, y, z + 1]),
                    xyz_to_i([x - 1, y, z]),
                    xyz_to_i([x, y - 1, z]),
                    xyz_to_i([x, y, z - 1])
                ]
                neighbor_indices_all[i] = neighborhood

                # Provide orthogonal spacing between labels
                if \
                        x % (self._resolution / label_resolution) == 0 and \
                        y % (self._resolution / label_resolution) == 0 and \
                        z % (self._resolution / label_resolution) == 0:
                    # Generate a label at this point
                    labeled_indices.append([point, i])

            else:

                if self.Debug_Constraints:
                    Debug(
                        self,
                        f".recalculate(): Point = {point}: Finally excluded with permeability = 0",
                        color=Theme.WarningColor,
                        force=True
                    )

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(100 * (i + 1) / n)

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): Interruption requested, exiting now", color=Theme.PrimaryColor)
                    return False

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        index_all_to_filtered = [-1] * n
        filtered_index = 0

        # Generate mapping from "all" indices to "filtered" indices
        for i, permeability in enumerate(permeabilities_all):
            if permeability == 0:
                continue

            index_all_to_filtered[i] = filtered_index
            filtered_index += 1

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        points_filtered = []
        permeabilities_filtered = []
        neighbor_indices_filtered = []

        # Filter for included points, i.e. those with permeability != 0; translate neighborhood indices
        for i, permeability in enumerate(permeabilities_all):
            if permeability == 0:
                continue

            point = points_all[i]
            permeability = permeabilities_all[i]

            # Translate neighborhood indices
            neighborhood = neighbor_indices_all[i]
            for j in range(6):
                if 0 <= neighborhood[j] < n:
                    if index_all_to_filtered[neighborhood[j]] != -1:
                        neighborhood[j] = index_all_to_filtered[neighborhood[j]]
                    else:
                        neighborhood[j] = -1    # Neighbor out of bounds
                else:
                    neighborhood[j] = -1        # Neighbor out of bounds

            points_filtered.append(point)
            permeabilities_filtered.append(permeability)
            neighbor_indices_filtered.append(neighborhood)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Translate label indices
        for i in range(len(labeled_indices)):
            labeled_indices[i][1] = index_all_to_filtered[labeled_indices[i][1]]

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self._points = np.array(points_filtered)
        self._permeabilities = np.array(permeabilities_filtered)
        self._labeled_indices = labeled_indices
        self._neighbor_indices = np.array(neighbor_indices_filtered)

        Debug(
            self,
            ".recalculate(): "
            f"Calculated {len(self.constraints)} constraints "
            f"over {n} possible points, "
            f"yielded {len(self._points)} points",
            color=Theme.PrimaryColor
        )

        if len(self._points) == 0:
            Debug(
                self,
                ".recalculate: USER WARNING: Avoiding empty sampling volume by adding origin",
                color=Theme.WarningColor,
                force=True
            )
            origin = np.zeros(3)
            self._points = np.array([origin])
            self._permeabilities = np.array([0])
            self._labeled_indices = [(origin, 0)]
            self._neighbor_indices = np.array([[0, 0, 0, 0, 0, 0]])

        progress_callback(100)

        return True
