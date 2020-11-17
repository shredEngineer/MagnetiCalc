""" Field module. """

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
from numba import jit, prange, set_num_threads
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.BiotSavart_CUDA import BiotSavart_CUDA
from magneticalc.BiotSavart_JIT import BiotSavart_JIT
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


class Field:
    """ Field class. """

    def __init__(self, backend: int, _type: int, distance_limit: float, length_scale: float):
        """
        Initializes an empty field.

        @param backend: Backend index (0: JIT; 1: JIT + CUDA)
        @param _type: Field type to display (0: A-field; 1: B-field)
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        """
        Debug(self, ": Init")

        self._backend = backend
        self._type = _type
        self._distance_limit = distance_limit
        self._length_scale = length_scale

        self._total_limited = None
        self._vectors = None

    def is_valid(self) -> bool:
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self._total_limited is not None and \
            self._vectors is not None

    def invalidate(self):
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._total_limited = None
        self._vectors = None

    def get_type(self) -> int:
        """
        Gets field type.

        @return: Field type (0: A-field; 1: B-field)
        """
        return self._type

    def get_units(self) -> str:
        """
        Gets field units.

        @return: Field units
        """
        return [
            "Tm",   # A-field: Tesla · meter
            "T"     # B-field: Tesla
        ][self._type]

    def get_vectors(self):
        """
        Gets field vectors. (The selected field type determined which field was calculated.)

        @return: Ordered list of 3D vectors (field vectors & corresponding sampling volume points have the same indices)
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated field")

        return self._vectors

    def get_total_limited(self) -> int:
        """
        Gets total number of distance limited points.

        @return: Total number of distance limited points
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated field")

        return self._total_limited

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self, wire, sampling_volume, progress_callback, num_cores: int) -> bool:
        """
        Recalculates field vectors.

        @param wire: Wire
        @param sampling_volume: Sampling volume
        @param progress_callback: Progress callback
        @param num_cores: Number of cores to use for multiprocessing
        @return: True if successful, False if interrupted (CUDA backend currently not interruptable)
        """

        # Default to JIT backend if CUDA backend is selected but not available
        if self._backend == 1:
            if not BiotSavart_CUDA.is_available():
                Debug(
                    self,
                    f".recalculate(): WARNING: CUDA backend not available, defaulting to JIT backend",
                    color=Theme.WarningColor,
                    force=True
                )
                self._backend = 0

        if self._backend == 0:

            # Initialize Biot-Savart JIT backend
            biot_savart = BiotSavart_JIT(
                self._type,
                self._distance_limit,
                self._length_scale,
                wire.get_dc(),
                wire.get_elements(),
                sampling_volume.get_points(),
                sampling_volume.get_permeabilities(),
                progress_callback
            )

            # Fetch result using Biot-Savart JIT backend
            set_num_threads(num_cores)
            tup = biot_savart.get_result()

        elif self._backend == 1:

            # Initialize Biot-Savart CUDA backend
            biot_savart = BiotSavart_CUDA(
                self._type,
                self._distance_limit,
                self._length_scale,
                wire.get_dc(),
                wire.get_elements(),
                sampling_volume.get_points(),
                sampling_volume.get_permeabilities(),
                progress_callback
            )

            # Fetch result using Biot-Savart JIT backend
            set_num_threads(num_cores)
            tup = biot_savart.get_result()

        else:

            Debug(self, f".recalculate(): No such backend: {self._backend}", color=Theme.WarningColor, force=True)
            return False

        # Handle interrupt
        if tup is None:
            return False

        self._total_limited = tup[0]
        self._vectors = tup[1]

        # Prints the sampling volume points, current elements and field vectors; may be used for debugging:
        """
        def print_array(array): return "np.array([" + ",".join([f"[{p[0]},{p[1]},{p[2]}]" for p in array]) + "])"

        element_centers = [element[0] for element in wire.get_elements()]
        element_directions = [element[1] for element in wire.get_elements()]

        import sys
        import numpy
        numpy.set_printoptions(threshold=sys.maxsize)

        print("sampling_volume_points =", print_array(sampling_volume.get_points()))
        print("element_centers        =", print_array(element_centers))
        print("element_directions     =", print_array(element_directions))
        print("vectors          =", print_array(self._vectors))
        """

        return True

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @jit(nopython=True, parallel=True)
    def get_arrows(
            sampling_volume_points,
            field_vectors,
            line_pairs,
            head_points,
            arrow_scale: float,
            magnitude_limit: float
    ):
        """
        Returns the field arrow parameters needed by L{VispyCanvas}.

        @param sampling_volume_points: Sampling volume points
        @param field_vectors: Field vectors
        @param line_pairs: Arrow line pairs (ordered list of arrow start/stop 3D points)
        @param head_points: Arrow head points (ordered list of arrow stop 3D points)
        @param arrow_scale: Arrow scale
        @param magnitude_limit: Magnitude limit (mitigating divisions by zero)
        """
        for i in prange(len(field_vectors)):

            # Calculate field vector magnitude (mitigating divisions by zero)
            field_vector_length = np.sqrt(
                field_vectors[i][0] ** 2 + field_vectors[i][1] ** 2 + field_vectors[i][2] ** 2
            )
            if field_vector_length < magnitude_limit:
                field_vector_length = magnitude_limit

            # Calculate normalized field direction
            field_direction_norm = field_vectors[i] / field_vector_length

            # Calculate arrow start & end coordinates
            p_start = sampling_volume_points[i] + field_direction_norm / 2 / 2 * arrow_scale
            p_end = sampling_volume_points[i] - field_direction_norm / 2 / 2 * arrow_scale

            # Populate arrow line & head coordinates
            line_pairs[2 * i + 0] = p_start
            line_pairs[2 * i + 1] = p_end
            head_points[i] = p_end

        return line_pairs, head_points
