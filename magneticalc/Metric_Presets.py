""" Metric_Presets module. """

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


class Metric_Presets:
    """ Metric_Presets class. """

    # Metric value: Magnitude in XYZ-space (linear)
    Magnitude = {
        "id"        : "Magnitude",
        "norm_id"   : "Radius",
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XY-plane (linear)
    MagnitudeXY = {
        "id"        : "Magnitude XY",
        "norm_id"   : "Radius XY",
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in X-direction (linear)
    MagnitudeX = {
        "id"        : "Magnitude X",
        "norm_id"   : "Radius X",
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Y-direction (linear)
    MagnitudeY = {
        "id"        : "Magnitude Y",
        "norm_id"   : "Radius Y",
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Z-direction (linear)
    MagnitudeZ = {
        "id"        : "Magnitude Z",
        "norm_id"   : "Radius Z",
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XZ-plane (linear)
    MagnitudeXZ = {
        "id"        : "Magnitude XZ",
        "norm_id"   : "Radius XZ",
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in YZ-plane (linear)
    MagnitudeYZ = {
        "id"        : "Magnitude YZ",
        "norm_id"   : "Radius YZ",
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XYZ-space (logarithmic)
    LogMagnitude = {
        "id"        : "Log Magnitude",
        "norm_id"   : "Radius",
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in X-direction (logarithmic)
    LogMagnitudeX = {
        "id"        : "Log Magnitude X",
        "norm_id"   : "Radius X",
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Y-direction (logarithmic)
    LogMagnitudeY = {
        "id"        : "Log Magnitude Y",
        "norm_id"   : "Radius Y",
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Z-direction (logarithmic)
    LogMagnitudeZ = {
        "id"        : "Log Magnitude Z",
        "norm_id"   : "Radius Z",
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XY-plane (logarithmic)
    LogMagnitudeXY = {
        "id"        : "Log Magnitude XY",
        "norm_id"   : "Radius XY",
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XZ-plane (logarithmic)
    LogMagnitudeXZ = {
        "id"        : "Log Magnitude XZ",
        "norm_id"   : "Radius XZ",
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Magnitude in YZ-plane (logarithmic)
    LogMagnitudeYZ = {
        "id"        : "Log Magnitude YZ",
        "norm_id"   : "Radius YZ",
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Angle in XY-plane
    AngleXY = {
        "id"        : "Angle XY",
        "norm_id"   : "Angle XY",
        "is_log"    : False,
        "is_angle"  : True,
        "colormap"  : 1  # cyclic
    }

    # Metric preset: Angle in XZ-plane
    AngleXZ = {
        "id"        : "Angle XZ",
        "norm_id"   : "Angle XZ",
        "is_log"    : False,
        "is_angle"  : True,
        "colormap"  : 1  # cyclic
    }

    # Metric preset: Angle in YZ-plane
    AngleYZ = {
        "id"        : "Angle YZ",
        "norm_id"   : "Angle YZ",
        "is_log"    : False,
        "is_angle"  : True,
        "colormap"  : 1  # cyclic
    }

    # ------------------------------------------------------------------------------------------------------------------

    # List of all above presets
    List = [
        Magnitude,
        MagnitudeX,
        MagnitudeY,
        MagnitudeZ,
        MagnitudeXY,
        MagnitudeXZ,
        MagnitudeYZ,
        LogMagnitude,
        LogMagnitudeX,
        LogMagnitudeY,
        LogMagnitudeZ,
        LogMagnitudeXY,
        LogMagnitudeXZ,
        LogMagnitudeYZ,
        AngleXY,
        AngleXZ,
        AngleYZ
    ]

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_by_id(_id_: str):
        """
        Selects a preset by name.

        @param _id_: Preset ID
        @return: Preset parameters (or None if ID not found)
        """
        for preset in Metric_Presets.List:
            if _id_ == preset["id"]:
                return preset
        return None
