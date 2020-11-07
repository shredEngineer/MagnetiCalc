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
from magneticalc.BiotSavart_JIT import BiotSavart_JIT
from magneticalc.Debug import Debug


class Field:
    """ Field class. """

    def __init__(self, backend, _type, distance_limit, length_scale):
        """
        Initializes an empty field.

        @param backend: Backend index
        @param _type: Field type (0: A-Field; 1: B-Field)
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param length_scale: Length scale (m)
        """
        Debug(self, ": Init")

        self._backend = backend
        self._type = _type
        self._distance_limit = distance_limit
        self._length_scale = length_scale

        self._vectors = None
        self._total_limited = None

    def is_valid(self):
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self._vectors is not None and \
            self._total_limited is not None

    def invalidate(self):
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._vectors = None
        self._total_limited = None

    def get_type(self):
        """
        Gets field type.

        @return: Field type (0: A-Field; 1: B-Field)
        """
        return self._type

    def get_units(self):
        """
        Gets field units.

        @return: Field units (string)
        """
        return ["Tm", "T"][self._type]

    def get_vectors(self):
        """
        Gets field vectors.

        @return: Ordered list of 3D vectors (field vectors & corresponding sampling volume points have the same indices)
        """
        return self._vectors

    def get_total_limited(self):
        """
        Gets total number of distance limited points.

        @return: Total number of distance limited points
        """
        return self._total_limited

    # ------------------------------------------------------------------------------------------------------------------

    def recalculate(self, wire, sampling_volume, progress_callback, num_cores):
        """
        Recalculate field vectors.

        @param wire: Wire
        @param sampling_volume: Sampling volume
        @param progress_callback: Progress callback
        @param num_cores: Number of cores to use for multiprocessing
        @return: True if successful, False if interrupted
        """

        use_jit = self._backend == 0
        use_cuda = self._backend == 1

        if use_jit:
            # Initialize Biot-Savart JIT backend
            biot_savart = BiotSavart_JIT(
                progress_callback,
                self._type,
                self._distance_limit,
                self._length_scale,
                wire.get_dc(),
                wire.get_elements(),
                sampling_volume.get_points()
            )

            # Fetch result using Biot-Savart JIT backend
            set_num_threads(num_cores)
            tup = biot_savart.get_vectors()
        elif use_cuda:
            Debug(self, f"Backend not supported: {self._backend}", color=(255, 0, 0))
            return False
        else:
            Debug(self, f"No such backend: {self._backend}", color=(255, 0, 0))
            return False

        # Handle interrupt
        if tup is None:
            return False

        self._vectors = tup[0]
        self._total_limited = tup[1]

        return True

    # ------------------------------------------------------------------------------------------------------------------

    def get_squared(self):
        """
        Returns the "squared" field scalar. Used by Metric for calculation of energy and self-inductance.

        @return: Float
        """
        return self._get_squared_worker(self.get_vectors())

    @staticmethod
    @jit(nopython=True, parallel=True)
    def _get_squared_worker(vectors):
        """
        Returns the "squared" field scalar. Used by Metric for calculation of energy and self-inductance.

        @param vectors: Ordered list of 3D vectors
        @return: Float
        """
        squared = 0
        for i in prange(len(vectors)):
            squared += np.dot(vectors[i], vectors[i])
        return squared

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @jit(nopython=True, parallel=True)
    def get_arrows(
            sampling_volume_points,
            field_vectors,
            line_pairs,
            head_points,
            arrow_scale,
            magnitude_limit
    ):
        """
        Returns the field arrow parameters needed by VispyCanvas.

        @param sampling_volume_points: Sampling volume points
        @param field_vectors: Field vectors
        @param line_pairs: Arrow line pairs (ordered list of arrow start/stop 3D points)
        @param head_points: Arrow head points (ordered list of arrow stop 3D points)
        @param arrow_scale: Arrow scale
        @param magnitude_limit: Magnitude limit (mitigating divisions by zero)
        """
        for i in prange(len(sampling_volume_points)):

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
