""" BiotSavart module. """

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
from functools import partial
from PyQt5.QtCore import QThread
from magneticalc.Debug import Debug
from magneticalc.Metric import Metric
from magneticalc.Theme import Theme


class BiotSavart:
    """
    Implements the Biot-Savart law for calculating the magnetic flux density.
    Employing static & class methods only, for better multiprocessing performance.
    """

    # Constant for Biot-Savart law
    k = 1e-7  # H / m

    # Class attributes
    _type = None
    dc = None
    current_elements = None
    sampling_volume_points = None
    distance_limit = None
    total_limited = None

    progress_callback = None

    @classmethod
    def init(cls, _type, dc, current_elements, sampling_volume_points, distance_limit, progress_callback):
        """
        Populates class attributes.

        @param _type: Field type (0: A-Field; 1: B-Field)
        @param dc: Wire current (A)
        @param current_elements: List of current elements (list of 3D vector pairs: (element center, element direction))
        @param sampling_volume_points: List of sampling volume points
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param progress_callback: Progress callback
        """
        cls._type = _type
        cls.dc = dc
        cls.current_elements = current_elements
        cls.sampling_volume_points = sampling_volume_points
        cls.distance_limit = distance_limit
        cls.total_limited = 0
        cls.progress_callback = progress_callback

    @staticmethod
    def worker(_type, current_elements, distance_limit, sampling_volume_point):
        """
        Calculates the magnetic flux density at some sampling volume point using the Biot-Savart law.

        @param _type: Field type (0: A-Field; 1: B-Field)
        @param current_elements: Ordered list of current elements (3D vector pairs: (element center, element direction))
        @param distance_limit: Distance limit (mitigating divisions by zero)
        @param sampling_volume_point: Sampling volume point (3D vector)
        @return: Magnetic flux density vector (3D vector)
        """
        vector = np.zeros(3)
        total_limited = 0

        for element_center, element_direction in current_elements:
            vector_distance = (sampling_volume_point - element_center) * Metric.LengthScale

            # Calculate distance (mitigating divisions by zero)
            scalar_distance = np.linalg.norm(vector_distance)
            if scalar_distance < distance_limit:
                scalar_distance = distance_limit
                total_limited += 1

            if _type == 0:
                # Calculate A-Field (vector potential)
                vector += element_direction / scalar_distance

            elif _type == 1:
                # Calculate B-Field (flux density)
                vector += np.cross(element_direction, vector_distance) / (scalar_distance ** 3)

        return vector, total_limited

    @classmethod
    def get_vectors(cls, pool):
        """
        Calculates the magnetic flux density at every point of the sampling volume.

        @return: (Ordered list of 3D vectors, total # of distance limited points) if successful, None if interrupted
        """
        Debug(cls, ".get_vectors()", color=Theme.PrimaryColor)

        # Map sampling volume points to worker method, passing type, current elements & distance limit as const. args
        result = pool.imap(
            partial(cls.worker, cls._type, cls.current_elements, cls.distance_limit),
            cls.sampling_volume_points
        )

        vectors = []
        total_limited = 0

        # Fetch resulting vectors
        for i, tup in enumerate(result):

            vectors.append(tup[0])
            total_limited += tup[1]

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                cls.progress_callback(100 * (i + 1) / len(cls.sampling_volume_points))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(cls, ": Interruption requested, exiting now", color=Theme.PrimaryColor)
                    return None

        # Apply Biot-Savart constant & wire current scaling
        vectors = np.array(vectors) * BiotSavart.k * BiotSavart.dc

        return vectors, total_limited
