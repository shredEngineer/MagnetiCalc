""" BiotSavart_CUDA module. """

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

import math
import numpy as np
from numba import cuda
from magneticalc.Constants import Constants
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


class BiotSavart_CUDA:
    """
    Implements the Biot-Savart law for calculating the magnetic flux density (B-field) and vector potential (A-field).
    """

    def __init__(
            self,
            _type: int,
            distance_limit: float,
            length_scale: float,
            dc: float,
            current_elements,
            sampling_volume_points,
            sampling_volume_permeabilities,
            progress_callback
    ):
        """
        Initializes the class attributes.

        @param _type: Field type (0: A-field; 1: B-field)
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        @param dc: Wire current (A)
        @param current_elements: Ordered list of current elements (pairs: [element center, element direction])
        @param sampling_volume_points: Ordered list of sampling volume points
        @param sampling_volume_permeabilities: Ordered list of sampling volume's relative permeabilities µ_r
        @param progress_callback: Progress callback
        """
        self._type = _type
        self._distance_limit = distance_limit
        self._length_scale = length_scale
        self._dc = dc
        self._current_elements = current_elements
        self._sampling_volume_points = sampling_volume_points
        self._sampling_volume_permeabilities = sampling_volume_permeabilities
        self._progress_callback = progress_callback

        self.total_limited = 0

    @staticmethod
    def is_available():
        """
        Indicates the availability of this backend.

        @return: True if this backend is available, False otherwise
        """
        return cuda.is_available()

    @staticmethod
    @cuda.jit
    def worker(
            _type,
            distance_limit,
            length_scale,
            element_centers,
            element_directions,
            sampling_volume_points,
            sampling_volume_permeabilities,
            field_vectors,
            total_limited
    ):
        """
        Applies the Biot-Savart law for calculating the magnetic flux density (B-field) or vector potential (A-field)
        for all sampling volume points.

        @param _type: Field type (0: A-field; 1: B-field)
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        @param element_centers: Ordered list of current elements centers
        @param element_directions: Ordered list of current elements directions
        @param sampling_volume_points: Sampling volume points
        @param sampling_volume_permeabilities: Ordered list of sampling volume's relative permeabilities µ_r
        @param field_vectors: Field vectors (output array)
        @param total_limited: Total number of limited points (output array with only one element)
        """

        # noinspection PyUnresolvedReferences
        sampling_volume_index = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x

        if sampling_volume_index >= sampling_volume_points.shape[0]:
            return

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
                total_limited[0] += 1

            if _type == 0:
                # Calculate A-field (vector potential)
                vector_x += element_directions[current_element_index][0] * length_scale / scalar_distance
                vector_y += element_directions[current_element_index][1] * length_scale / scalar_distance
                vector_z += element_directions[current_element_index][2] * length_scale / scalar_distance
            elif _type == 1:
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

    def get_result(self):
        """
        Calculates the field at every point of the sampling volume.

        @return: (Total number of limited points, field) (currently non-interruptable)
        """
        Debug(self, ".get_result()", color=Theme.PrimaryColor)

        element_centers = [element[0] for element in self._current_elements]
        element_directions = [element[1] for element in self._current_elements]

        element_centers_global = cuda.to_device(element_centers)
        element_directions_global = cuda.to_device(element_directions)

        sampling_volume_points_global = cuda.to_device(self._sampling_volume_points)
        sampling_volume_permeabilities_global = cuda.to_device(self._sampling_volume_permeabilities)

        field_vectors_global = cuda.device_array((len(self._sampling_volume_points), 3))
        total_limited_global = cuda.device_array(1)

        TPB = 1024   # Maximum threads per block
        BPG = 65536  # Maximum blocks per grid

        BiotSavart_CUDA.worker[BPG, TPB](
            self._type,
            self._distance_limit,
            self._length_scale,
            element_centers_global,
            element_directions_global,
            sampling_volume_points_global,
            sampling_volume_permeabilities_global,
            field_vectors_global,
            total_limited_global
        )

        field_vectors_local = field_vectors_global.copy_to_host()
        total_limited_local = total_limited_global.copy_to_host()

        if self._type == 0 or self._type == 1:
            # Field is A-field or B-field
            field_vectors_local = field_vectors_local * self._dc * Constants.mu_0 / 4 / np.pi

        self._progress_callback(100)

        return int(total_limited_local[0]), field_vectors_local
