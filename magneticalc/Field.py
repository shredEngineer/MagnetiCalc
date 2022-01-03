""" Field module. """

#  ISC License
#
#  Copyright (c) 2020–2021, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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

from typing import Tuple, Callable
import numpy as np
from numba import jit, prange, set_num_threads
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Backend_Types import BACKEND_JIT, BACKEND_CUDA
from magneticalc.Backend_CUDA import Backend_CUDA
from magneticalc.Backend_JIT import Backend_JIT
from magneticalc.ConditionalDecorator import ConditionalDecorator
from magneticalc.Config import get_jit_enabled
from magneticalc.Debug import Debug
from magneticalc.Field_Types import A_FIELD, B_FIELD
from magneticalc.SamplingVolume import SamplingVolume
from magneticalc.Wire import Wire


class Field:
    """ Field class. """

    def __init__(self, backend_type: int, field_type: int, distance_limit: float, length_scale: float) -> None:
        """
        Initializes an empty field.

        @param backend_type: Backend type
        @param field_type: Field type
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        """
        Debug(self, ": Init")

        self._backend_type = backend_type
        self._field_type = field_type
        self._distance_limit = distance_limit
        self._length_scale = length_scale

        self._total_calculations = None
        self._total_skipped_calculations = None
        self._vectors = None

    def is_valid(self) -> bool:
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self._total_calculations is not None and \
            self._total_skipped_calculations is not None and \
            self._vectors is not None

    def invalidate(self) -> None:
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()")

        self._total_calculations = None
        self._total_skipped_calculations = None
        self._vectors = None

    def get_type(self) -> int:
        """
        Gets field type.

        @return: Field type
        """
        return self._field_type

    def get_units(self, show_gauss=False) -> Tuple[str, float]:
        """
        Gets field units.

        @param show_gauss: Enable to show Gauss instead of Tesla
        @return: Field units, field factor
        """
        if show_gauss:
            return {
                A_FIELD: "Gs·m",    # Gauss · meter
                B_FIELD: "Gs"       # Gauss
            }.get(self._field_type, None), 1e4
        else:
            return {
                A_FIELD: "T·m",     # Tesla · meter
                B_FIELD: "T"        # Tesla
            }.get(self._field_type, None), 1e0

    def get_vectors(self) -> np.ndarray:
        """
        Gets field vectors. (The selected field type determined which field was calculated.)

        @return: Ordered list of 3D vectors (field vectors & corresponding sampling volume points have the same indices)
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated field")

        return self._vectors

    def get_total_calculations(self) -> int:
        """
        Gets total number of calculations.

        @return: Total number of calculations
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated field")

        return self._total_calculations

    def get_total_skipped_calculations(self) -> int:
        """
        Gets total number of skipped calculations.

        @return: Total number of skipped calculations
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated field")

        return self._total_skipped_calculations

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(
            self,
            wire: Wire,
            sampling_volume: SamplingVolume,
            progress_callback: Callable,
            num_cores: int
    ) -> bool:
        """
        Recalculates field vectors.

        @param wire: Wire
        @param sampling_volume: Sampling volume
        @param progress_callback: Progress callback
        @param num_cores: Number of cores to use for multiprocessing
        @return: True if successful, False if interrupted (CUDA backend currently not interruptable)
        """
        Debug(self, ".recalculate()")

        # Compute the current elements.
        current_elements = wire.get_elements()

        # Default to JIT backend if CUDA backend is selected but not available.
        if self._backend_type == BACKEND_CUDA:
            if not Backend_CUDA.is_available():
                Debug(
                    self, f".recalculate(): WARNING: CUDA backend not available, defaulting to JIT backend",
                    warning=True
                )
                self._backend_type = BACKEND_JIT

        if self._backend_type == BACKEND_JIT:

            # Initialize Biot-Savart JIT backend
            backend = Backend_JIT(
                self._field_type,
                self._distance_limit,
                self._length_scale,
                wire.get_dc(),
                current_elements,
                sampling_volume.get_points(),
                sampling_volume.get_permeabilities(),
                progress_callback
            )

            # Fetch result using Biot-Savart JIT backend
            set_num_threads(num_cores)
            backend_result = backend.get_result()

        elif self._backend_type == BACKEND_CUDA:

            # Initialize Biot-Savart CUDA backend
            backend = Backend_CUDA(
                self._field_type,
                self._distance_limit,
                self._length_scale,
                wire.get_dc(),
                current_elements,
                sampling_volume.get_points(),
                sampling_volume.get_permeabilities(),
                progress_callback
            )

            # Fetch result using Biot-Savart CUDA backend
            set_num_threads(num_cores)
            backend_result = backend.get_result()

        else:

            Debug(self, f".recalculate(): ERROR: No such backend: {self._backend_type}", error=True)
            return False

        # Handle interrupt
        if backend_result is None:
            return False

        self._total_calculations = backend_result[0]
        self._total_skipped_calculations = backend_result[1]
        self._vectors = backend_result[2]

        # Sanity check
        expected_total_calculations = len(current_elements) * sampling_volume.get_points_count()
        if expected_total_calculations != self._total_calculations:
            Assert_Dialog(False, "ERROR: Unexpected number of calculations – Backend seems to be buggy")
            return False

        return True

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @ConditionalDecorator(get_jit_enabled(), jit, nopython=True, parallel=True)
    def get_arrows(
            sampling_volume_points: np.ndarray,
            field_vectors: np.ndarray,
            line_pairs: np.ndarray,
            head_points: np.ndarray,
            arrow_scale: float,
            magnitude_limit: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns the field arrow parameters needed by L{VispyCanvas}.

        @param sampling_volume_points: Sampling volume points
        @param field_vectors: Field vectors
        @param line_pairs: Arrow line pairs (ordered list of arrow start/stop 3D points)
        @param head_points: Arrow head points (ordered list of arrow stop 3D points)
        @param arrow_scale: Arrow scale
        @param magnitude_limit: Magnitude limit (mitigating divisions by zero)
        @return: Line pairs, head points
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
