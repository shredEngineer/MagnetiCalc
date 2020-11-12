""" Perspective_Presets module. """

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


class Perspective_Presets:
    """ Perspective_Presets class. """

    # Preset: Isometric
    Isometric = {
        "id": "Isometric",
        "azimuth": 135,
        "elevation": np.arctan(1 / np.sqrt(2)) * 180 / np.pi
    }

    # Preset: XY-plane
    PlaneXY = {
        "id": "Plane XY",
        "azimuth": 0,
        "elevation": 90
    }

    # Preset: XZ-plane
    PlaneXZ = {
        "id": "Plane XZ",
        "azimuth": 0,
        "elevation": 0
    }

    # Preset: YZ-plane
    PlaneYZ = {
        "id": "Plane YZ",
        "azimuth": 90,
        "elevation": 0
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

    @staticmethod
    def get_by_id(_id_: str):
        """
        Selects a preset by name.

        @param _id_: Preset ID
        @return: Preset parameters (or None if ID not found)
        """
        for preset in Perspective_Presets.List:
            if _id_ == preset["id"]:
                return preset
        return None
