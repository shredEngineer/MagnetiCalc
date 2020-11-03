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

    def __init__(self, _type, distance_limit):
        """
        Initializes an empty field.

        @param _type: Field type (0: A-Field; 1: B-Field)
        @param distance_limit: Distance limit (mitigating divisions by zero)
        """
        Debug(self, ": Init")

        self._type = _type
        self._distance_limit = distance_limit

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
            self._type,
            wire.get_dc(),
            wire.get_elements(),
            sampling_volume.get_points(),
            self._distance_limit,
            progress_callback
        )

        # Fetch multiprocessing result
        with Pool(num_cores) as pool:
            tup = biot_savart.get_vectors(pool)

        # Handle interrupt
        if tup is None:
            return False

        self._vectors = tup[0]
        self._total_limited = tup[1]

        return True
