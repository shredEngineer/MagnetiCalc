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

from multiprocessing import Pool
from magneticalc.BiotSavart import BiotSavart
from magneticalc.Debug import Debug


class Field:
    """ Field class. """

    def __init__(self):
        """ Initializes an empty field. """
        Debug(self, ": Init")

        self._vectors = None

    def is_valid(self):
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return self._vectors is not None

    def invalidate(self):
        """ Resets data, hiding from display. """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._vectors = None

    def get_vectors(self):
        """
        Get field vectors.

        @return: List of 3D vectors
        """
        return self._vectors

    def recalculate(self, wire, sampling_volume, progress_callback, num_cores):
        """
        Recalculate field vectors.

        @param wire: Wire
        @param sampling_volume: Sampling volume
        @param progress_callback: Progress callback
        @param num_cores: Number of cores to use for multiprocessing
        @return: True if successful, False if interrupted
        """
        biot_savart = BiotSavart()

        # Initialize Biot-Savart class
        biot_savart.init(
            wire.get_dc(),
            wire.get_elements(),
            sampling_volume.get_points(),
            progress_callback
        )

        # Fetch multiprocessing result
        with Pool(num_cores) as pool:
            vectors = biot_savart.get_vectors(pool)

        # Handle interrupt
        if vectors is None:
            return False

        self._vectors = vectors

        return True
