""" Metric module. """

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
import matplotlib.cm as cm
from matplotlib.colors import Normalize, LogNorm
from PyQt5.QtCore import QThread
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Debug import Debug


class Metric:
    """
    Provides different metrics, mapping some field vector properties to some color and alpha range.
    For a list of color maps, see: https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
    """

    # Length scale
    LengthScale = 1e-2  # m  (== 1 cm)

    # Cutoff for logarithmic scaling
    LogNormMinimum = 1e-12

    # Metric value: Magnitude in XYZ-space (linear)
    Magnitude = {
        "id": "Magnitude",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(point),
        "log": False,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric value: Magnitude in XY-plane (linear)
    MagnitudeXY = {
        "id": "Magnitude XY",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(np.array([point[0], point[1]])),
        "log": False,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric value: Magnitude in XZ-plane (linear)
    MagnitudeXZ = {
        "id": "Magnitude XZ",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(np.array([point[0], point[2]])),
        "log": False,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric value: Magnitude in YZ-plane (linear)
    MagnitudeYZ = {
        "id": "Magnitude YZ",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(np.array([point[1], point[2]])),
        "log": False,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric value: Magnitude in XYZ-space (logarithmic)
    LogMagnitude = {
        "id": "Log Magnitude",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(point),
        "log": True,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric value: Magnitude in XY-plane (logarithmic)
    LogMagnitudeXY = {
        "id": "Log Magnitude XY",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(np.array([point[0], point[1]])),
        "log": True,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric value: Magnitude in XZ-plane (logarithmic)
    LogMagnitudeXZ = {
        "id": "Log Magnitude XZ",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(np.array([point[0], point[2]])),
        "log": True,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric preset: Magnitude in YZ-plane (logarithmic)
    LogMagnitudeYZ = {
        "id": "Log Magnitude YZ",
        "func": lambda point: Metric.LengthScale * np.linalg.norm(np.array([point[1], point[2]])),
        "log": True,
        "is_angle": False,
        "colormap": cm.cool  # divergent
    }

    # Metric preset: Angle in XY-plane
    AngleXY = {
        "id": "Angle XY",
        "func": lambda point: (np.arctan2(point[0], point[1]) + np.pi) / np.pi / 2,
        "log": False,
        "is_angle": True,
        "colormap": cm.hsv  # cyclic
    }

    # Metric preset: Angle in XZ-plane
    AngleXZ = {
        "id": "Angle XZ",
        "func": lambda point: (np.arctan2(point[0], point[2]) + np.pi) / np.pi / 2,
        "log": False,
        "is_angle": True,
        "colormap": cm.hsv  # cyclic
    }

    # Metric preset: Angle in YZ-plane
    AngleYZ = {
        "id": "Angle YZ",
        "func": lambda point: (np.arctan2(point[1], point[2]) + np.pi) / np.pi / 2,
        "log": False,
        "is_angle": True,
        "colormap": cm.hsv  # cyclic
    }

    # List of all above presets
    Presets = [
        Magnitude,
        MagnitudeXY,
        MagnitudeXZ,
        MagnitudeYZ,
        LogMagnitude,
        LogMagnitudeXY,
        LogMagnitudeXZ,
        LogMagnitudeYZ,
        AngleXY,
        AngleXZ,
        AngleYZ
    ]

    @staticmethod
    def get_by_id(_id_):
        """
        Selects a preset by name.

        @param _id_: Preset ID string
        @return: Preset parameters (or None if ID not found)
        """
        for preset in Metric.Presets:
            if _id_ == preset["id"]:
                return preset
        return None

    def __init__(self, color_preset, alpha_preset):
        """
        This class holds a pair of metric presets.
        Using these metric presets, colors (including alpha channel) and field limits are calculated.

        @param color_preset: Color metric preset (dictionary)
        @param alpha_preset: Alpha metric preset (dictionary)
        """
        Debug(self, ": Init")

        self._color_preset = color_preset
        self._alpha_preset = alpha_preset

        self._colors = None
        self._limits = None

    def is_valid(self):
        """
        Indicates valid data for display.

        @return: True if data is valid for display, False otherwise
        """
        return \
            self._colors is not None and \
            self._limits is not None

    def invalidate(self):
        """
        Resets data, hiding from display.
        """
        Debug(self, ".invalidate()", color=(128, 0, 0))

        self._colors = None
        self._limits = None

    def get_color_preset(self):
        """
        Returns color metric preset.

        @return: Color metric preset (dictionary)
        """
        return self._color_preset

    def get_alpha_preset(self):
        """
        Returns alpha metric preset.

        @return: Alpha metric preset (dictionary)
        """
        return self._alpha_preset

    def get_colors(self):
        """
        Returns calculated colors.

        @return: List of color values (4-tuples)
        """
        return self._colors

    def get_limits(self):
        """
        Returns calculated limits.

        @return: Dictionary
        """
        return self._limits

    def recalculate(self, field_vectors, progress_callback):
        """
        Recalculate color and alpha values for field.

        @param field_vectors: Field vectors
        @param progress_callback: Progress callback
        @return: True if successful, False if interrupted
        """
        Debug(self, ".recalculate()", color=(0, 128, 0))

        # Calculate color and alpha metric values
        color_values = np.zeros(len(field_vectors))
        alpha_values = np.zeros(len(field_vectors))
        for i in range(len(field_vectors)):
            color_values[i] = self._color_preset["func"](field_vectors[i])
            alpha_values[i] = self._alpha_preset["func"](field_vectors[i])

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(10 * (i + 1) / len(field_vectors))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): Interruption requested, exiting now", color=(0, 0, 255))
                    return False

        # Select color range
        if self._color_preset["is_angle"]:
            color_min, color_max = 0, 1
        else:
            color_min, color_max = min(color_values), max(color_values)

        # Select alpha range
        if self._alpha_preset["is_angle"]:
            alpha_min, alpha_max = 0, 1
        else:
            alpha_min, alpha_max = min(alpha_values), max(alpha_values)

        # Select color normalizer
        if self._color_preset["log"]:
            Assert_Dialog(not self._color_preset["is_angle"], "Logarithmic angles don't make any sense")

            # Adjust range for logarithm (out-of-range values will be clipped in the loop below)
            color_min_ = max(color_min, Metric.LogNormMinimum)   # avoiding "ValueError: minvalue must be positive"
            color_max_ = max(color_min_, color_max)              # avoiding "ValueError: minvalue must be <= maxvalue"

            color_normalize = LogNorm(vmin=color_min_, vmax=color_max_)
        else:
            color_min_ = color_min
            color_max_ = color_max
            color_normalize = Normalize(vmin=color_min_, vmax=color_max_)

        # Select alpha normalizer
        if self._alpha_preset["log"]:
            Assert_Dialog(not self._alpha_preset["is_angle"], "Logarithmic angles don't make any sense")

            # Adjust range for logarithm (out-of-range values will be clipped in the loop below)
            alpha_min_ = max(alpha_min, Metric.LogNormMinimum)   # avoiding "ValueError: minvalue must be positive"
            alpha_max_ = max(alpha_min_, alpha_max)              # avoiding "ValueError: minvalue must be <= maxvalue"

            alpha_normalize = LogNorm(vmin=alpha_min_, vmax=alpha_max_)
        else:
            alpha_min_ = alpha_min
            alpha_max_ = alpha_max
            alpha_normalize = Normalize(vmin=alpha_min_, vmax=alpha_max_)

        # (1) Calculate color and alpha normalization
        # (2) Calculate colormap and assemble final color/alpha values
        #     Note: Of course, the alpha metric colormap is ignored
        colors = np.zeros([len(field_vectors), 4])
        for i in range(len(field_vectors)):

            # Calculate normalized color and alpha values
            # Note: If using logarithmic scaling, out-of-range values (still exceeding [0...1] here) may be clipped
            color_value_normalized = color_normalize(color_values[i], clip=True)
            alpha_value_normalized = alpha_normalize(alpha_values[i], clip=True)

            colors[i] = self._color_preset["colormap"](color_value_normalized)
            colors[i][3] = alpha_value_normalized

            # Signal progress update, handle interrupt (every 16 iterations to keep overhead low)
            if i & 0xf == 0:
                progress_callback(10 + 90 * (i + 1) / len(field_vectors))

                if QThread.currentThread().isInterruptionRequested():
                    Debug(self, ".recalculate(): Interruption requested, exiting now", color=(0, 0, 255))
                    return False

        self._colors = colors

        self._limits = {
            "color_min": color_min,
            "color_max": color_max,
            "alpha_min": alpha_min,
            "alpha_max": alpha_max
        }

        return True
