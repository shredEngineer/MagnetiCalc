""" Backend_JIT module. """

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
import numpy as np
from numba import jit, prange
from PyQt5.QtCore import QThread
from magneticalc.ConditionalDecorator import ConditionalDecorator
from magneticalc.Config import get_jit_enabled
from magneticalc.Constants import Constants
from magneticalc.Debug import Debug
from magneticalc.Field_Types import A_FIELD, B_FIELD


class Backend_JIT:
    """
    Implements the Biot-Savart law for calculating the magnetic flux density (B-field) and vector potential (A-field).
    Backend: JIT.
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
    @ConditionalDecorator(get_jit_enabled(), jit, nopython=True, parallel=True)
    def worker(
            field_type: int,
            distance_limit: float,
            length_scale: float,
            current_elements: np.ndarray,
            sampling_volume_point: np.ndarray
    ) -> Optional[Tuple[int, int, np.ndarray]]:
        """
        Applies the Biot-Savart law for calculating the magnetic flux density (B-field) or vector potential (A-field)
        for a single sampling volume point.

        @param field_type: Field type
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        @param current_elements: Ordered list of current elements (pairs: [element center, element direction])
        @param sampling_volume_point: Sampling volume point
        @return: (Total # of calculations, total # of skipped calculations, vector)
        """
        total_calculations = 0
        total_skipped_calculations = 0
        vector = np.zeros(3)

        for j in prange(len(current_elements)):

            element_center = current_elements[j][0]
            element_direction = current_elements[j][1]

            vector_distance = (sampling_volume_point - element_center) * length_scale

            # Calculate distance (mitigating divisions by zero)
            scalar_distance = np.sqrt(vector_distance[0] ** 2 + vector_distance[1] ** 2 + vector_distance[2] ** 2)
            if scalar_distance < distance_limit:
                scalar_distance = distance_limit
                total_skipped_calculations += 1

            total_calculations += 1

            if field_type == A_FIELD:
                # Calculate A-field (vector potential)
                vector += element_direction * length_scale / scalar_distance
            elif field_type == B_FIELD:
                # Calculate B-field (flux density)
                vector += np.cross(element_direction * length_scale, vector_distance) / (scalar_distance ** 3)

        return total_calculations, total_skipped_calculations, vector

    def get_result(self) -> Optional[Tuple[int, int, np.ndarray]]:
        """
        Calculates the field at every point of the sampling volume.

        @return: (Total # of calculations, total # of skipped calculations, field) if successful, None if interrupted
        """
        Debug(self, ".get_result()")

        total_calculations = 0
        total_skipped_calculations = 0
        vectors = []

        # Fetch resulting vectors
        for i in range(len(self._sampling_volume_points)):

            tup = Backend_JIT.worker(
                self._field_type,
                self._distance_limit,
                self._length_scale,
                self._current_elements,
                self._sampling_volume_points[i]
            )

            total_calculations += tup[0]
            total_skipped_calculations += tup[1]
            vector = tup[2] * self._sampling_volume_permeabilities[i]

            vectors.append(vector)

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                self._progress_callback(100 * (i + 1) / len(self._sampling_volume_points))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".get_result(): WARNING: Interruption requested, exiting now", warning=True)
                    return None

        if self._field_type == A_FIELD or self._field_type == B_FIELD:
            vectors = np.array(vectors) * self._dc * Constants.mu_0 / 4 / np.pi

        self._progress_callback(100)

        return total_calculations, total_skipped_calculations, vectors
