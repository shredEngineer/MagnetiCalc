""" Sampling volume module. """

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

from typing import Tuple, List, Callable, Dict
import numpy as np
from PyQt5.QtCore import QThread
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Constraint import Constraint
from magneticalc.Debug import Debug
from magneticalc.Validatable import Validatable, require_valid, validator


class SamplingVolume(Validatable):
    """ Sampling volume class. """

    # Enable to show additional debug info during constraint calculation
    Debug_Constraints = False

    def __init__(self) -> None:
        """
        Initializes an empty sampling volume, with zero bounds and no constraints.
        """
        Validatable.__init__(self)
        Debug(self, ": Init", init=True)

        self._bounds_min = np.zeros(3)
        self._bounds_max = np.zeros(3)
        self._dimension: Tuple[int, int, int] = (0, 0, 0)

        self._points = np.array([])
        self._permeabilities = np.array([])
        self._labeled_indices: List = []
        self._neighbor_indices: List[np.ndarray] = []

        self.resolution = 0
        self._label_resolution = 0
        self._constraints = []

    def set(
            self,
            resolution: float,
            label_resolution: float,
            constraints: List[Constraint]
    ) -> None:
        """
        Sets the parameters.

        @param resolution: Resolution
        @param label_resolution: Label resolution
        @param constraints: List of constraints
        """
        self.resolution = resolution
        self._label_resolution = label_resolution
        self._constraints = constraints

        Assert_Dialog(resolution > 0, "Resolution must be > 0")
        Assert_Dialog(label_resolution > 0, "Label resolution must be > 0")

    @property
    def bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns this volume's bounding box.

        @return: _bounds_min, _bounds_max
        """
        return self._bounds_min, self._bounds_max

    @property
    def extent(self) -> List:
        """
        Returns this volume's extent.

        @return: 3D point
        """
        return self._bounds_max - self._bounds_min

    def set_bounds_nearest(self, bounds: np.ndarray) -> None:
        """
        Adjusts this volume's bounding box to fully enclose a 3D wire curve.
        This expands the bounding box to the next integer grid coordinates.

        Note: This will not automatically invalidate the sampling volume.

        @param bounds: Bounding box (minimum bounds, maximum bounds)
        @return: Rounded (_bounds_min, _bounds_max)
        """
        self._bounds_min = np.array([np.floor(x) for x in bounds[0]])
        self._bounds_max = np.array([np.ceil(x) for x in bounds[1]])

    def set_padding_nearest(self, padding: np.ndarray) -> None:
        """
        Shrinks or enlarges this volume's bounding box by some amount, in each direction, symmetrically.
        This shrinks or expands the bounding box to the next integer grid coordinates.

        Note: This will not automatically invalidate the sampling volume.

        @param padding: Amount of padding (3D point)
        """
        self._bounds_min -= np.array([np.floor(x) for x in padding])
        self._bounds_max += np.array([np.ceil(x) for x in padding])

    # ------------------------------------------------------------------------------------------------------------------

    @validator
    def recalculate(self, progress_callback: Callable) -> bool:
        """
        Recalculates the sampling volume points, permeabilities, labels and neighborhoods according to the constraints.

        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()")

        # Group constraints by permeability
        constraints_precedence_dict: Dict = {}
        for constraint in self._constraints:
            if constraint.permeability in constraints_precedence_dict:
                constraints_precedence_dict[constraint.permeability].append(constraint)
            else:
                constraints_precedence_dict[constraint.permeability] = [constraint]

        if self.Debug_Constraints:
            Debug(self, f".recalculate(): Created {len(constraints_precedence_dict)} constraint group(s)")

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Calculate all possible grid points
        points_axes_all = [[], [], []]
        for i in range(3):
            steps = np.ceil((self._bounds_max[i] - self._bounds_min[i]) * self.resolution).astype(int) + 1
            points_axes_all[i] = np.linspace(self._bounds_min[i], self._bounds_max[i], steps)

        self._dimension = np.array([len(axis) for axis in points_axes_all])
        n = self._dimension[0] * self._dimension[1] * self._dimension[2]

        points_all = np.zeros(shape=(n, 3))
        permeabilities_all = np.zeros(n)
        neighbor_indices_all = [[0, 0, 0, 0, 0, 0]] * n

        labeled_indices = []

        def i_to_xyz(_i: int) -> List:
            """
            Convert 1D index to 3D indices.

            @param _i: 1D index
            @return: 3D indices
            """
            _x = _i % self._dimension[0]
            _y = (_i // self._dimension[0]) % self._dimension[1]
            _z = _i // (self._dimension[0] * self._dimension[1])
            return [_x, _y, _z]

        def xyz_to_i(xyz: List) -> int:
            """
            Convert 3D indices to 1D index.

            @param xyz: 3D indices
            @return: 1D index
            """
            return xyz[0] + xyz[1] * self._dimension[0] + xyz[2] * self._dimension[0] * self._dimension[1]

        # Linearly iterate through all possible grid points, computing the 3D cartesian ("euclidean") product
        for i in range(n):

            x, y, z = i_to_xyz(i)

            point = np.array([points_axes_all[0][x], points_axes_all[1][y], points_axes_all[2][z]])

            permeability = 1.0  # Default relative permeability for unconstrained points

            # Iterate over constraint groups of descending permeability; higher permeabilities take precedence
            for permeability_key in sorted(constraints_precedence_dict, reverse=True):

                included = True

                if self.Debug_Constraints:
                    Debug(
                        self,
                        f".recalculate(): Point = {point}: "
                        f"Calculating {len(constraints_precedence_dict[permeability_key])} constraint(s) "
                        f"for permeability = {permeability_key} …"
                    )

                # Calculate the inclusion relation for the current group
                for constraint in constraints_precedence_dict[permeability_key]:

                    if not constraint.evaluate(point):

                        if self.Debug_Constraints:
                            Debug(self, f".recalculate(): Point = {point}: Constraint evaluated to False (breaking)")

                        # Exclude this point within the current group
                        included = False
                        break

                    else:

                        if self.Debug_Constraints:
                            Debug(self, f".recalculate(): Point = {point}: Constraint evaluated to True", success=True)

                if included:

                    if self.Debug_Constraints:
                        Debug(self, f".recalculate(): Point = {point}: Included by precedence grouping", success=True)

                    permeability = permeability_key
                    break

                else:

                    if self.Debug_Constraints:
                        Debug(self, f".recalculate(): Point = {point}: Excluded by precedence grouping")

            if permeability != 0:

                if self.Debug_Constraints:
                    Debug(self, f".recalculate(): Point = {point}: Finally included with permeability = {permeability}")

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
                        np.fmod(x, self.resolution / self._label_resolution) == 0 and \
                        np.fmod(y, self.resolution / self._label_resolution) == 0 and \
                        np.fmod(z, self.resolution / self._label_resolution) == 0:
                    # Generate a label at this point
                    labeled_indices.append([point, i])

            else:

                if self.Debug_Constraints:
                    Debug(self, f".recalculate(): Point = {point}: Finally excluded with permeability = 0")

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(100 * (i + 1) / n)

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): WARNING: Interruption requested, exiting now", warning=True)
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
            f"{len(self._constraints)} constraints left {n} of {len(self._points)} possible points"
        )

        if len(self._points) == 0:
            Debug(self, ".recalculate: USER WARNING: Avoiding empty sampling volume by adding origin", warning=True)
            origin = np.zeros(3)
            self._points = np.array([origin])
            self._permeabilities = np.array([0])
            self._labeled_indices = [(origin, 0)]
            self._neighbor_indices = np.array([[0, 0, 0, 0, 0, 0]])

        progress_callback(100)

        return True

    @property
    @require_valid
    def dimension(self) -> Tuple[int, int, int]:
        """
        @return: Sampling volume dimension if it is valid, None otherwise.
        """
        return self._dimension

    @property
    @require_valid
    def points(self) -> np.array:
        """
        Returns this sampling volume's points.

        @return: Array of 3D points
        """
        return self._points

    @property
    @require_valid
    def points_count(self) -> int:
        """
        Returns this sampling volume's point count.

        @return: Point count
        """
        return len(self._points)

    @property
    @require_valid
    def permeabilities(self) -> np.ndarray:
        """
        Returns this sampling volume's relative permeabilities µ_r.

        @return: Ordered list of sampling volume's relative permeabilities µ_r
        """
        return self._permeabilities

    @property
    @require_valid
    def labeled_indices(self) -> List:
        """
        Returns this sampling volume's labeled indices.

        @return: Unordered list of pairs [sampling volume point, field index]
        """
        return self._labeled_indices

    @property
    @require_valid
    def labels_count(self) -> int:
        """
        Returns this sampling volume's label count.

        @return: Label count
        """
        return len(self._labeled_indices)

    @property
    @require_valid
    def neighbor_indices(self) -> List[np.ndarray]:
        """
        Returns this sampling volume's neighborhood indices.

        @return: Ordered list of sampling volume neighborhood indices (six 3D vectors)
        """
        return self._neighbor_indices
