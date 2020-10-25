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


class BiotSavart:
    """
    Implements the Biot-Savart law for calculating the magnetic flux density.
    Employing static & class methods only, for better multiprocessing performance.
    """

    # Constant for Biot-Savart law, in SI units
    k = 1e-7  # H / m

    # Divisor cutoff (avoiding divisions by zero)
    DivisorCutoff = 1e-12

    # Class attributes
    dc = None
    current_elements = None
    sampling_volume_points = None
    progress_callback = None

    @classmethod
    def init(cls, dc, current_elements, sampling_volume_points, progress_callback):
        """
        Populates class attributes.

        @param dc: DC factor
        @param current_elements: List of current elements (list of 3D vector pairs: (element center, element direction))
        @param sampling_volume_points: List of sampling volume points
        @param progress_callback: Progress callback
        """
        cls.dc = dc
        cls.current_elements = current_elements
        cls.sampling_volume_points = sampling_volume_points
        cls.progress_callback = progress_callback

    @staticmethod
    def worker(current_elements, sampling_volume_point):
        """
        Calculates the magnetic flux density at some sampling volume point using the Biot-Savart law.

        @param current_elements: List of current elements (list of 3D vector pairs: (element center, element direction))
        @param sampling_volume_point: Sampling volume point (3D vector)
        @return: Magnetic flux density vector (3D vector)
        """
        vector = np.zeros(3)

        for element_center, element_direction in current_elements:
            vector_distance = (sampling_volume_point - element_center) * Metric.LengthScale
            scalar_distance_cubed = np.linalg.norm(vector_distance) ** 3

            # Avoiding divisions by zero
            if scalar_distance_cubed < BiotSavart.DivisorCutoff:
                continue

            vector += np.cross(element_direction, vector_distance) / scalar_distance_cubed

        return vector

    @classmethod
    def get_vectors(cls, pool):
        """
        Calculates the magnetic flux density at every point of the sampling volume.

        @return: List of vectors if successful, None if interrupted
        """
        Debug(cls, ".get_vectors()", color=(0, 0, 255))

        # Map sampling volume points to worker function, passing current elements as constant argument
        result = pool.imap(partial(cls.worker, cls.current_elements), cls.sampling_volume_points)

        vectors = []

        # Fetch resulting vectors
        for i, point in enumerate(result):

            vectors.append(point)

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                cls.progress_callback(100 * (i + 1) / len(cls.sampling_volume_points))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(cls, ": Interruption requested, exiting now", color=(0, 0, 255))
                    return None

        # Apply Biot-Savart constant scaling and DC factor
        vectors = np.array(vectors) * BiotSavart.k * BiotSavart.dc

        return vectors
