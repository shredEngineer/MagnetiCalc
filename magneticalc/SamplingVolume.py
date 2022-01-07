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

from typing import Tuple, List, Callable
import numpy as np
from PyQt5.QtCore import QThread
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Constraint import Constraint
from magneticalc.Debug import Debug
from magneticalc.Validatable import Validatable, require_valid, validator


class SamplingVolume(Validatable):
    """ Sampling volume class. """

    def __init__(self) -> None:
        """
        Initializes an empty sampling volume, with zero bounds and no constraints.
        """
        Validatable.__init__(self)
        Debug(self, ": Init", init=True)

        self._bounds_min: np.ndarray = np.zeros(3)
        self._bounds_max: np.ndarray = np.zeros(3)
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

    def _i_to_xyz(self, _i: int) -> List:
        """
        Convert 1D index to 3D indices.
        Note: "Fortran" indexing (column-major order).

        @param _i: 1D index
        @return: 3D indices
        """
        return [
            _i % self._dimension[0],
            (_i // self._dimension[0]) % self._dimension[1],
            _i // (self._dimension[0] * self._dimension[1])
        ]

    def _xyz_to_i(self, xyz: List) -> int:
        """
        Convert 3D indices to 1D index.
        Note: "Fortran" indexing (column-major order).

        @param xyz: 3D indices
        @return: 1D index
        """
        return xyz[0] + xyz[1] * self._dimension[0] + xyz[2] * self._dimension[0] * self._dimension[1]

    # ------------------------------------------------------------------------------------------------------------------

    @validator
    def recalculate(self, progress_callback: Callable) -> bool:
        """
        Recalculates the sampling volume points, permeabilities, labels and neighborhoods according to the constraints.

        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()")

        # Gather permeabilities by descending permeability
        permeability_groups = sorted(set([constraint.permeability for constraint in self._constraints]), reverse=True)

        # Group constraints by descending permeability
        Permeability_Groups_Precedence_Map = {
            permeability: [constraint for constraint in self._constraints if permeability == constraint.permeability]
            for permeability in permeability_groups
        }
        Debug(
            self,
            ".set(): Permeability groups: { " +
            ", ".join([
                f"µ_r={permeability} ({len(constraints)})"
                for permeability, constraints in Permeability_Groups_Precedence_Map.items()
            ]) + " }"
        )

        # Calculate all possible grid points
        total_axes = [
            np.linspace(
                self._bounds_min[i],
                self._bounds_max[i],
                np.ceil((self._bounds_max[i] - self._bounds_min[i]) * self.resolution).astype(int) + 1
            )
            for i in range(3)
        ]

        self._dimension = np.array([len(axis) for axis in total_axes])
        total_count = np.prod(self._dimension)
        total_points = np.zeros(shape=(total_count, 3))
        total_permeabilities = np.zeros(total_count)
        total_neighbor_indices = np.zeros(shape=(total_count, 6), dtype=int)
        labeled_indices = []

        # Linearly iterate through all possible grid points, computing the 3D cartesian ("euclidean") product
        for i in range(total_count):
            x, y, z = self._i_to_xyz(i)
            point = np.array([total_axes[0][x], total_axes[1][y], total_axes[2][z]])

            point_permeability = 1.0  # Default relative permeability for unconstrained points

            # Iterate over constraints grouped by descending permeability (higher permeabilities take precedence)
            # and calculate the inclusion relation for every group, breaking on the first match.
            for permeability, constraints in Permeability_Groups_Precedence_Map.items():
                if all([constraint.evaluate(point) for constraint in constraints]):
                    point_permeability = permeability
                    break

            if point_permeability != 0:
                # Include this point
                total_points[i] = point
                total_permeabilities[i] = point_permeability

                # Generate this sampling volume point's neighborhood
                neighborhood = [
                    self._xyz_to_i([x + 1, y, z]),
                    self._xyz_to_i([x, y + 1, z]),
                    self._xyz_to_i([x, y, z + 1]),
                    self._xyz_to_i([x - 1, y, z]),
                    self._xyz_to_i([x, y - 1, z]),
                    self._xyz_to_i([x, y, z - 1])
                ]
                total_neighbor_indices[i] = neighborhood

                # Provide orthogonal spacing between labels
                if \
                        np.fmod(x, self.resolution / self._label_resolution) == 0 and \
                        np.fmod(y, self.resolution / self._label_resolution) == 0 and \
                        np.fmod(z, self.resolution / self._label_resolution) == 0:
                    # Generate a label at this point
                    labeled_indices.append([point, i])

            # Signal progress update, handle interrupt (every 256 iterations to keep overhead low)
            if i & 0xff == 0:
                progress_callback(100 * (i + 1) / total_count)

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): WARNING: Interruption requested, exiting now", warning=True)
                    return False

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        index_all_to_filtered = [-1] * total_count
        filtered_index = 0

        # Generate mapping from "all" indices to "filtered" indices
        for i, permeability in enumerate(total_permeabilities):
            if permeability == 0:
                continue

            index_all_to_filtered[i] = filtered_index
            filtered_index += 1

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        points_filtered = []
        permeabilities_filtered = []
        neighbor_indices_filtered = []

        # Filter for included points, i.e. those with permeability != 0; translate neighborhood indices
        for i, permeability in enumerate(total_permeabilities):
            if permeability == 0:
                continue

            point = total_points[i]
            permeability = total_permeabilities[i]

            # Translate neighborhood indices
            neighborhood = total_neighbor_indices[i]
            for j in range(6):
                if 0 <= neighborhood[j] < total_count:
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
            f"{len(self._constraints)} constraints left {len(self._points)} of {total_count} possible points"
        )

        if len(self._points) == 0:
            Debug(self, ".recalculate: WARNING: Avoiding empty sampling volume by adding origin", warning=True)
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
