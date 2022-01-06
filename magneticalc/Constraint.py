""" Constraint module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm <anfrage@paulwilhelm.de>
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

from magneticalc.Norm_Types import *
from typing import Union, List
import numpy as np
from magneticalc.Metric import metric_norm
from magneticalc.Comparison_Types import *


class Constraint:
    """ Constraint class. """

    """ Supported norm types. """
    Norm_Types_Supported = [
        NORM_TYPE_X,
        NORM_TYPE_Y,
        NORM_TYPE_Z,
        NORM_TYPE_RADIUS,
        NORM_TYPE_RADIUS_X,
        NORM_TYPE_RADIUS_Y,
        NORM_TYPE_RADIUS_Z,
        NORM_TYPE_RADIUS_XY,
        NORM_TYPE_RADIUS_XZ,
        NORM_TYPE_RADIUS_YZ,
        NORM_TYPE_ANGLE_XY,
        NORM_TYPE_ANGLE_XZ,
        NORM_TYPE_ANGLE_YZ
    ]

    """ Supported norm types using minimum and maximum angles in degrees. """
    Norm_Types_Supported_Degrees = [
        NORM_TYPE_ANGLE_XY,
        NORM_TYPE_ANGLE_XZ,
        NORM_TYPE_ANGLE_YZ
    ]

    """ Supported comparison types. """
    Comparison_Types_Supported = [
        COMPARISON_TYPE_IN_RANGE
    ]

    def __init__(self, norm_type: int, comparison_type: int, _min: float, _max: float, permeability: float):
        """
        Initializes the constraint.

        @param norm_type: Norm type
        @param comparison_type: Comparison type
        @param _min: Minimum value
        @param _max: Maximum value
        @param permeability: Relative permeability µ_r
        """
        norm_type = norm_type_safe(norm_type)
        comparison_type = comparison_type_safe(comparison_type)

        self._is_angle = norm_type in self.Norm_Types_Supported_Degrees

        self._norm_type = norm_type
        self._comparison_type = comparison_type

        self._min = _min
        self._max = _max

        self.permeability = permeability

    def evaluate(self, point: Union[np.ndarray, List[float]]) -> bool:
        """
        Evaluate this constraint at some point.

        @param point: Point (3D vector)
        """
        norm = metric_norm(self._norm_type, point)

        # Perform comparison
        if self._comparison_type == COMPARISON_TYPE_IN_RANGE:

            if self._is_angle:
                # Convert normalized angle to degrees
                norm *= 360

            return self._min <= norm <= self._max

        else:
            # Invalid comparison ID
            return False
