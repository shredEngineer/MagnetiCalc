""" Parameters module. """

#  ISC License
#
#  Copyright (c) 2020, Paul Wilhelm <anfrage@paulwilhelm.de>
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
from numba import jit, prange
from magneticalc.Constants import Constants
from magneticalc.Debug import Debug
from magneticalc.Metric import Metric
from magneticalc.Theme import Theme


class Parameters:
    """ Parameters class. """

    def __init__(self):
        """
        Initializes parameters class.
        """
        Debug(self, ": Init")

        self._energy = None
        self._self_inductance = None
        self._magnetic_dipole_moment = None

    def is_valid(self) -> bool:
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        # Note: Not checking _energy and _self_inductance as these are not always calculated (only for B-field)
        return \
            self._magnetic_dipole_moment is not None

    def invalidate(self):
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._energy = None
        self._self_inductance = None
        self._magnetic_dipole_moment = None

    def get_energy(self) -> float:
        """
        Returns calculated energy.

        @return: Float
        """
        return self._energy

    def get_self_inductance(self) -> float:
        """
        Returns calculated self-inductance.

        @return: Float
        """
        return self._self_inductance

    def get_magnetic_dipole_moment(self) -> float:
        """
        Returns calculated magnetic dipole moment.

        @return: Float
        """
        return self._magnetic_dipole_moment

    # ------------------------------------------------------------------------------------------------------------------

    def get_squared_field(self, sampling_volume, field) -> float:
        """
        Returns the "squared" field scalar.

        @param sampling_volume: SamplingVolume
        @param field: B-field
        @return: Float
        """
        return self._get_squared_field_worker(sampling_volume.get_permeabilities(), field.get_vectors())

    @staticmethod
    @jit(nopython=True, parallel=True)
    def _get_squared_field_worker(sampling_volume_permeabilities, field_vectors) -> float:
        """
        Returns the "squared" field scalar.

        @param sampling_volume_permeabilities: Ordered list of sampling volume's relative permeabilities µ_r
        @param field_vectors: Ordered list of 3D vectors (B-field)
        @return: Float
        """
        squared = 0
        for i in prange(len(field_vectors)):
            squared += np.dot(field_vectors[i], field_vectors[i] / sampling_volume_permeabilities[i])
        return squared

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _get_magnetic_dipole_moment(self, wire, length_scale: float) -> float:
        """
        Returns the magnetic dipole moment scalar.

        @param wire: Wire
        @param length_scale: Length scale (m)
        @return: Float
        """
        elements_center = np.array([element[0] for element in wire.get_elements()])
        elements_direction = np.array([element[1] for element in wire.get_elements()])
        vector = self._get_magnetic_dipole_moment_worker(elements_center, elements_direction, length_scale)
        return np.abs(wire.get_dc() * np.linalg.norm(vector) / 2)

    @staticmethod
    @jit(nopython=True, parallel=True)
    def _get_magnetic_dipole_moment_worker(elements_center, elements_direction, length_scale: float):
        """
        Returns the (unscaled) magnetic dipole moment vector.

        @param elements_center: Current element centers
        @param elements_direction: Current element directions
        @param length_scale: Length scale (m)
        @return: Magnetic dipole moment vector
        """
        squared = np.zeros(3)
        for i in prange(len(elements_center)):
            squared += np.cross(elements_center[i] * length_scale, elements_direction[i] * length_scale)
        return squared

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def recalculate(self, wire, sampling_volume, field, progress_callback) -> bool:
        """
        Recalculates parameters.

        @param wire: Wire
        @param sampling_volume: SamplingVolume
        @param field: Field
        @param progress_callback: Progress callback
        @return: True (currently non-interruptable)
        """
        Debug(self, ".recalculate()", color=Theme.SuccessColor)

        progress_callback(0)

        self._magnetic_dipole_moment = self._get_magnetic_dipole_moment(wire, Metric.LengthScale)

        progress_callback(33)

        if field.get_type == 0:

            # Field is A-field
            pass

        elif field.get_type() == 1:

            # Field is B-field

            dV = (Metric.LengthScale / sampling_volume.get_resolution()) ** 3  # Sampling volume element
            self._energy = self.get_squared_field(sampling_volume, field) * dV / Constants.mu_0

            progress_callback(66)

            self._self_inductance = self._energy / np.square(wire.get_dc())

        progress_callback(100)

        return True
