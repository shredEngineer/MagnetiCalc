""" Perspective_Presets module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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

from typing import Dict
import numpy as np
from magneticalc.Assert_Dialog import Assert_Dialog


class Perspective_Presets:
    """ Perspective_Presets class. """

    # Preset: Isometric
    Isometric = {
        "id": "Isometric",
        "azimuth": 135.0,
        "elevation": round(np.arctan(1 / np.sqrt(2)) * 180 / np.pi, 4)
    }

    # Preset: XY-plane
    PlaneXY = {
        "id": "Plane XY",
        "azimuth": 0.0,
        "elevation": 90.0
    }

    # Preset: XZ-plane
    PlaneXZ = {
        "id": "Plane XZ",
        "azimuth": 0.0,
        "elevation": 0.0
    }

    # Preset: YZ-plane
    PlaneYZ = {
        "id": "Plane YZ",
        "azimuth": 90.0,
        "elevation": 0.0
    }

    # ------------------------------------------------------------------------------------------------------------------

    # List of all above presets
    List = [
        Isometric,
        PlaneXY,
        PlaneXZ,
        PlaneYZ
    ]

    # ------------------------------------------------------------------------------------------------------------------

    Fallback = Isometric

    @staticmethod
    def get_by_id(_id_: str) -> Dict:
        """
        Selects a preset by name.

        @param _id_: Preset ID
        @return: Preset parameters
        """
        for preset in Perspective_Presets.List:
            if _id_ == preset["id"]:
                return preset

        Assert_Dialog(False, f"Invalid perspective preset ID: Defaulting to \"{Perspective_Presets.Fallback['id']}\"")
        return Perspective_Presets.Fallback
