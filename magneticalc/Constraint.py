""" Constraint module. """

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
from magneticalc.Debug import Debug
from magneticalc.Metric import metric_norm


class Constraint:
    """ Constraint class. """

    # Norm IDs
    Norm_ID_List = {
        "x"         : 0,
        "y"         : 1,
        "z"         : 2,
        "radius_xy" : 3,
        "radius_yz" : 4,
        "radius_zx" : 5,
        "radius"    : 6,
        "angle_xy"  : 7,
        "angle_xz"  : 8,
        "angle_yz"  : 9,
    }

    # Comparison IDs
    Comparison_ID_List = {
        "range"     : 0
    }

    def __init__(self, norm_id, comparison_id, _min, _max):
        """
        Initializes the constraint.

        @param norm_id: Norm ID (string)
        @param comparison_id: Comparison ID (string)
        @param _min: Minimum value
        @param _max: Maximum value
        """
        if norm_id not in self.Norm_ID_List:
            Debug(self, "Invalid norm ID", color=(255, 0, 0))
            return

        if comparison_id not in self.Comparison_ID_List:
            Debug(self, "Invalid comparison ID", color=(255, 0, 0))
            return

        self._norm_id = norm_id
        self._comparison_id = comparison_id

        self._min = _min
        self._max = _max

    def evaluate(self, point):
        """
        Evaluate this constraint at some point.

        @param point: Point (3D vector)
        """
        norm = metric_norm(self._norm_id, point)

        # Perform comparison
        if self._comparison_id == "range":
            return self._min <= norm <= self._max
        else:
            # Invalid comparison ID
            return False
