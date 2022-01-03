""" Backend_CUDA module. """

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

from typing import Callable, Tuple, Optional
import math
import numpy as np
from numba import cuda
from PyQt5.QtCore import QThread
from magneticalc.Constants import Constants
from magneticalc.Debug import Debug
from magneticalc.Field_Types import A_FIELD, B_FIELD


class Backend_CUDA:
    """
    Implements the Biot-Savart law for calculating the magnetic flux density (B-field) and vector potential (A-field).
    Backend: JIT + CUDA.
    """

    def __init__(
            self,
            field_type: int,
            distance_limit: float,
            length_scale: float,
            dc: float,
            current_elements: np.ndarray,
            sampling_volume_points: np.ndarray,
            sampling_volume_permeabilities: np.ndarray,
            progress_callback: Callable
    ) -> None:
        """
        Initializes the class attributes.

        @param field_type: Field type
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        @param dc: Wire current (A)
        @param current_elements: Ordered list of current elements (pairs: [element center, element direction])
        @param sampling_volume_points: Ordered list of sampling volume points
        @param sampling_volume_permeabilities: Ordered list of sampling volume's relative permeabilities µ_r
        @param progress_callback: Progress callback
        """
        Debug(self, ": Init")

        self._field_type = field_type
        self._distance_limit = distance_limit
        self._length_scale = length_scale
        self._dc = dc
        self._current_elements = current_elements
        self._sampling_volume_points = sampling_volume_points
        self._sampling_volume_permeabilities = sampling_volume_permeabilities
        self._progress_callback = progress_callback

    @staticmethod
    def is_available() -> bool:
        """
        Indicates the availability of this backend.

        @return: True if this backend is available, False otherwise
        """
        return cuda.is_available()

    @staticmethod
    @cuda.jit
    def worker(
            field_type: int,
            distance_limit: float,
            length_scale: float,
            element_centers: np.ndarray,
            element_directions: np.ndarray,
            sampling_volume_points: np.ndarray,
            sampling_volume_permeabilities: np.ndarray,
            field_vectors: np.ndarray,
            total_calculations: np.ndarray,
            total_skipped_calculations: np.ndarray
    ) -> None:
        """
        Applies the Biot-Savart law for calculating the magnetic flux density (B-field) or vector potential (A-field)
        for all sampling volume points.

        @param field_type: Field type
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        @param element_centers: Ordered list of current elements centers
        @param element_directions: Ordered list of current elements directions
        @param sampling_volume_points: Sampling volume points
        @param sampling_volume_permeabilities: Ordered list of sampling volume's relative permeabilities µ_r
        @param field_vectors: Field vectors (output array)
        @param total_calculations: Total number of calculations (output array)
        @param total_skipped_calculations: Total number of skipped calculations (output array)
        """

        # noinspection PyUnresolvedReferences
        sampling_volume_index = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x

        if sampling_volume_index >= sampling_volume_points.shape[0]:
            return

        total_calculations[sampling_volume_index] = 0
        total_skipped_calculations[sampling_volume_index] = 0

        vector_x = 0
        vector_y = 0
        vector_z = 0

        for current_element_index in range(element_centers.shape[0]):
            vector_distance_x = (sampling_volume_points[sampling_volume_index][0] -
                                 element_centers[current_element_index][0]) * length_scale
            vector_distance_y = (sampling_volume_points[sampling_volume_index][1] -
                                 element_centers[current_element_index][1]) * length_scale
            vector_distance_z = (sampling_volume_points[sampling_volume_index][2] -
                                 element_centers[current_element_index][2]) * length_scale

            # Calculate distance (mitigating divisions by zero)
            scalar_distance = math.sqrt(vector_distance_x ** 2 + vector_distance_y ** 2 + vector_distance_z ** 2)
            if scalar_distance < distance_limit:
                scalar_distance = distance_limit
                total_skipped_calculations[sampling_volume_index] += 1

            total_calculations[sampling_volume_index] += 1

            if field_type == A_FIELD:

                # Calculate A-field (vector potential)
                vector_x += element_directions[current_element_index][0] * length_scale / scalar_distance
                vector_y += element_directions[current_element_index][1] * length_scale / scalar_distance
                vector_z += element_directions[current_element_index][2] * length_scale / scalar_distance

            elif field_type == B_FIELD:

                # Calculate B-field (flux density)
                a_1 = element_directions[current_element_index][0] * length_scale
                a_2 = element_directions[current_element_index][1] * length_scale
                a_3 = element_directions[current_element_index][2] * length_scale
                vector_x += (a_2 * vector_distance_z - a_3 * vector_distance_y) / (scalar_distance ** 3)
                vector_y += (a_3 * vector_distance_x - a_1 * vector_distance_z) / (scalar_distance ** 3)
                vector_z += (a_1 * vector_distance_y - a_2 * vector_distance_x) / (scalar_distance ** 3)

        field_vectors[sampling_volume_index, 0] = vector_x * sampling_volume_permeabilities[sampling_volume_index]
        field_vectors[sampling_volume_index, 1] = vector_y * sampling_volume_permeabilities[sampling_volume_index]
        field_vectors[sampling_volume_index, 2] = vector_z * sampling_volume_permeabilities[sampling_volume_index]

    def get_result(self) -> Optional[Tuple[int, int, np.ndarray]]:
        """
        Calculates the field at every point of the sampling volume.

        @return: (Total # of calculations, total # of skipped calculations, field) if successful, None if interrupted
        """
        Debug(self, ".get_result()")

        element_centers = [element[0] for element in self._current_elements]
        element_directions = [element[1] for element in self._current_elements]

        element_centers_global = cuda.to_device(element_centers)
        element_directions_global = cuda.to_device(element_directions)

        total_calculations = 0
        total_skipped_calculations = 0
        field_vectors = np.zeros(shape=(0, 3))

        # Split the calculation into chunks for progress update and interruption handling
        chunk_size_max = 1024 * 16
        chunk_start = 0
        remaining = len(self._sampling_volume_points)

        while remaining > 0:

            if remaining >= chunk_size_max:
                chunk_size = chunk_size_max
            else:
                chunk_size = remaining

            sampling_volume_points_global = cuda.to_device(
                self._sampling_volume_points[chunk_start:chunk_start + chunk_size]
            )
            sampling_volume_permeabilities_global = cuda.to_device(
                self._sampling_volume_permeabilities[chunk_start:chunk_start + chunk_size]
            )

            # Signal progress update, handle interrupt
            self._progress_callback(100 * chunk_start / len(self._sampling_volume_points))

            if QThread.currentThread().isInterruptionRequested():
                Debug(self, ".get_result(): WARNING: Interruption requested, exiting now", warning=True)
                return None

            remaining -= chunk_size
            chunk_start += chunk_size

            total_calculations_global = cuda.to_device(np.zeros(chunk_size))
            total_skipped_calculations_global = cuda.to_device(np.zeros(chunk_size))
            field_vectors_global = cuda.device_array((chunk_size, 3))

            TPB = 1024   # Maximum threads per block
            BPG = 65536  # Maximum blocks per grid

            Backend_CUDA.worker[BPG, TPB](
                self._field_type,
                self._distance_limit,
                self._length_scale,
                element_centers_global,
                element_directions_global,
                sampling_volume_points_global,
                sampling_volume_permeabilities_global,
                field_vectors_global,
                total_calculations_global,
                total_skipped_calculations_global
            )

            total_calculations_local = total_calculations_global.copy_to_host()
            total_skipped_calculations_local = total_skipped_calculations_global.copy_to_host()
            field_vectors_local = field_vectors_global.copy_to_host()

            if self._field_type == A_FIELD or self._field_type == B_FIELD:
                # Field is A-field or B-field
                field_vectors_local = field_vectors_local * self._dc * Constants.mu_0 / 4 / np.pi

            total_calculations += int(sum(total_calculations_local))
            total_skipped_calculations += int(sum(total_skipped_calculations_local))
            field_vectors = np.append(field_vectors, field_vectors_local, axis=0)

        self._progress_callback(100)

        return total_calculations, total_skipped_calculations, np.array(field_vectors)
