""" Metric_Presets module. """

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

from magneticalc.Norm_Types import *
from typing import Dict
from magneticalc.Assert_Dialog import Assert_Dialog


class Metric_Presets:
    """ Metric_Presets class. """

    # Metric value: Magnitude in XYZ-space (linear)
    Magnitude = {
        "id"        : "Magnitude",
        "norm_type" : NORM_TYPE_RADIUS,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in X-direction (linear)
    MagnitudeX = {
        "id"        : "Magnitude X",
        "norm_type" : NORM_TYPE_RADIUS_X,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Y-direction (linear)
    MagnitudeY = {
        "id"        : "Magnitude Y",
        "norm_type" : NORM_TYPE_RADIUS_Y,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Z-direction (linear)
    MagnitudeZ = {
        "id"        : "Magnitude Z",
        "norm_type" : NORM_TYPE_RADIUS_Z,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XY-plane (linear)
    MagnitudeXY = {
        "id"        : "Magnitude XY",
        "norm_type" : NORM_TYPE_RADIUS_XY,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XZ-plane (linear)
    MagnitudeXZ = {
        "id"        : "Magnitude XZ",
        "norm_type" : NORM_TYPE_RADIUS_XZ,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in YZ-plane (linear)
    MagnitudeYZ = {
        "id"        : "Magnitude YZ",
        "norm_type" : NORM_TYPE_RADIUS_YZ,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Unipolar Divergence (linear)
    Divergence = {
        "id"        : "Divergence",
        "norm_type" : NORM_TYPE_DIVERGENCE,
        "polarity"  : 0,
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Negative Divergence (linear)
    NegDivergence = {
        "id"        : "Divergence –",
        "norm_type" : NORM_TYPE_DIVERGENCE,
        "polarity"  : -1,
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Positive Divergence (linear)
    PosDivergence = {
        "id"        : "Divergence +",
        "norm_type" : NORM_TYPE_DIVERGENCE,
        "polarity"  : +1,
        "is_log"    : False,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XYZ-space (logarithmic)
    LogMagnitude = {
        "id"        : "Log Magnitude",
        "norm_type" : NORM_TYPE_RADIUS,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in X-direction (logarithmic)
    LogMagnitudeX = {
        "id"        : "Log Magnitude X",
        "norm_type" : NORM_TYPE_RADIUS_X,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Y-direction (logarithmic)
    LogMagnitudeY = {
        "id"        : "Log Magnitude Y",
        "norm_type" : NORM_TYPE_RADIUS_Y,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in Z-direction (logarithmic)
    LogMagnitudeZ = {
        "id"        : "Log Magnitude Z",
        "norm_type" : NORM_TYPE_RADIUS_Z,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XY-plane (logarithmic)
    LogMagnitudeXY = {
        "id"        : "Log Magnitude XY",
        "norm_type" : NORM_TYPE_RADIUS_XY,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric value: Magnitude in XZ-plane (logarithmic)
    LogMagnitudeXZ = {
        "id"        : "Log Magnitude XZ",
        "norm_type" : NORM_TYPE_RADIUS_XZ,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Magnitude in YZ-plane (logarithmic)
    LogMagnitudeYZ = {
        "id"        : "Log Magnitude YZ",
        "norm_type" : NORM_TYPE_RADIUS_YZ,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Unipolar Divergence (logarithmic)
    LogDivergence = {
        "id"        : "Log Divergence",
        "norm_type" : NORM_TYPE_DIVERGENCE,
        "polarity"  : 0,
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Positive Divergence (logarithmic)
    PosLogDivergence = {
        "id"        : "Log Divergence +",
        "norm_type" : NORM_TYPE_DIVERGENCE,
        "polarity"  : +1,
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Negative Divergence (logarithmic)
    NegLogDivergence = {
        "id"        : "Log Divergence –",
        "norm_type" : NORM_TYPE_DIVERGENCE,
        "polarity"  : -1,
        "is_log"    : True,
        "is_angle"  : False,
        "colormap"  : 0  # divergent
    }

    # Metric preset: Angle in XY-plane
    AngleXY = {
        "id"        : "Angle XY",
        "norm_type" : NORM_TYPE_ANGLE_XY,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : True,
        "colormap"  : 1  # cyclic
    }

    # Metric preset: Angle in XZ-plane
    AngleXZ = {
        "id"        : "Angle XZ",
        "norm_type" : NORM_TYPE_ANGLE_XZ,
        "polarity"  : 0,  # currently only used for divergence
        "is_log"    : False,
        "is_angle"  : True,
        "colormap"  : 1  # cyclic
    }

    # Metric preset: Angle in YZ-plane
    AngleYZ = {
        "id"        : "Angle YZ",
        "norm_type" : NORM_TYPE_ANGLE_YZ,
        "polarity"  : 0,  # currently only used for divergence
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
        Divergence,
        PosDivergence,
        NegDivergence,
        LogMagnitude,
        LogMagnitudeX,
        LogMagnitudeY,
        LogMagnitudeZ,
        LogMagnitudeXY,
        LogMagnitudeXZ,
        LogMagnitudeYZ,
        LogDivergence,
        PosLogDivergence,
        NegLogDivergence,
        AngleXY,
        AngleXZ,
        AngleYZ,
    ]

    # ------------------------------------------------------------------------------------------------------------------

    Fallback = Magnitude

    @staticmethod
    def get_by_id(_id_: str) -> Dict:
        """
        Selects a preset by name.

        @param _id_: Preset ID
        @return: Preset parameters
        """
        for preset in Metric_Presets.List:
            if _id_ == preset["id"]:
                return preset

        Assert_Dialog(False, f"Invalid metric preset ID: Defaulting to \"{Metric_Presets.Fallback['id']}\"")
        return Metric_Presets.Fallback
