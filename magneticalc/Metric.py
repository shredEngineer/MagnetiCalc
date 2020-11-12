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
from numba import jit, prange
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Constants import Constants
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme


@jit(nopython=True, parallel=False)
def metric_norm(norm_id: str, vector):
    """
    Calculates the selected norm of some vector.

    Note: For JIT to work, this must be declared at the top level.

    @param norm_id: Norm ID
    @param vector: 3D vector
    """
    if norm_id == "X":
        value = vector[0]
    elif norm_id == "Y":
        value = vector[1]
    elif norm_id == "Z":
        value = vector[2]
    elif norm_id == "Radius X":
        value = np.abs(vector[0])
    elif norm_id == "Radius Y":
        value = np.abs(vector[1])
    elif norm_id == "Radius Z":
        value = np.abs(vector[2])
    elif norm_id == "Radius XY":
        value = np.sqrt(vector[0] ** 2 + vector[1] ** 2)
    elif norm_id == "Radius XZ":
        value = np.sqrt(vector[1] ** 2 + vector[2] ** 2)
    elif norm_id == "Radius YZ":
        value = np.sqrt(vector[2] ** 2 + vector[0] ** 2)
    elif norm_id == "Radius":
        value = np.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
    elif norm_id == "Angle XY":
        value = (np.arctan2(vector[0], vector[1]) + np.pi) / np.pi / 2
    elif norm_id == "Angle XZ":
        value = (np.arctan2(vector[0], vector[2]) + np.pi) / np.pi / 2
    elif norm_id == "Angle YZ":
        value = (np.arctan2(vector[1], vector[2]) + np.pi) / np.pi / 2
    else:
        # Invalid norm ID
        value = None

    return value


@jit(nopython=True, parallel=False)
def color_map_divergent(color_normalized: float) -> (float, float, float):
    """
    Maps normalized value to color, divergent.

    Note: For JIT to work, this must be declared at the top level.

    @param color_normalized: Normalized color value
    @return: R, G, B
    """
    rgb_0 = np.array([0x00, 0xff, 0xfe]) / 255
    rgb_1 = np.array([0xff, 0x22, 0xf9]) / 255
    return rgb_0 + (rgb_1 - rgb_0) * color_normalized


@jit(nopython=True, parallel=False)
def color_map_cyclic(color_normalized: float) -> (float, float, float):
    """
    Maps normalized value to color, cyclic.

    Note: For JIT to work, this must be declared at the top level.

    @param color_normalized: Normalized color value
    @return: R, G, B
    """
    hue = (color_normalized + 1 / 6) % 1
    x = hue * 6
    r = 1 if 0 <= x <= 1 or 5 <= x <= 6 else x - 4 if 4 <= x <= 5 else 2 - x if 1 <= x <= 2 else 0
    g = 1 if 1 <= x <= 3 else x if 0 <= x <= 1 else 4 - x if 3 <= x <= 4 else 0
    b = 1 if 3 <= x <= 5 else x - 2 if 2 <= x <= 3 else 6 - x if 5 <= x <= 6 else 0
    return np.array([r, g, b])


class Metric:
    """
    Provides different metrics, used for mapping some field vector properties to some color and alpha range.
    """

    # Length scale
    LengthScale = 1e-2  # m  (1 cm)

    # Minimum argument limit for logarithmic scaling
    LogNormMinimum = 1e-12

    # ------------------------------------------------------------------------------------------------------------------

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

    def is_valid(self) -> bool:
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
        Assert_Dialog(self.is_valid(), "Accessing invalidated metric")

        return self._colors

    def get_limits(self):
        """
        Returns calculated limits.

        @return: Dictionary
        """
        Assert_Dialog(self.is_valid(), "Accessing invalidated metric")

        return self._limits

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @jit(nopython=True, parallel=True)
    def _norm_worker(norm_color: str, norm_alpha: str, vectors):
        """
        Calculates color and alpha norm values.

        @param norm_color: Color norm ID
        @param norm_alpha: Alpha norm ID
        @param vectors: Ordered list of 3D vectors
        @return: Color norm values, alpha norm values
        """
        color_values = np.zeros(len(vectors))
        alpha_values = np.zeros(len(vectors))

        for i in prange(len(vectors)):
            color_values[i] = metric_norm(norm_color, vectors[i])
            alpha_values[i] = metric_norm(norm_alpha, vectors[i])

        return color_values, alpha_values

    @staticmethod
    @jit(nopython=True, parallel=True)
    def _normalize_worker(
            color_map_id: str,
            color_is_log: bool,
            color_norm_values,
            color_norm_min: float,
            color_norm_max: float,
            alpha_is_log: bool,
            alpha_norm_values,
            alpha_norm_min: float,
            alpha_norm_max: float,
            colors
    ):
        """
        Normalizes color and alpha norm values, populates final color values.

        @param color_map_id: Color map ID
        @param color_is_log: Selects logarithmic normalizer for color
        @param color_norm_values: Color norm values
        @param color_norm_min: Minimum color norm value
        @param color_norm_max: Maximum color norm value
        @param alpha_is_log: Selects logarithmic normalizer for alpha
        @param alpha_norm_values: Alpha norm values
        @param alpha_norm_min: Minimum alpha norm value
        @param alpha_norm_max: Maximum alpha norm value
        @param colors: Color value list to populate (list of 4D vectors)
        @return: Color values (list of 4D vectors)
        """

        # (1) Calculate color and alpha normalization
        # (2) Calculate colormap and assemble final color/alpha values
        #     Note: Of course, the alpha metric colormap is ignored

        for i in prange(len(color_norm_values)):

            color_normalized = color_norm_values[i]

            # Clip before normalizing, needed for logarithmic normalization
            if color_normalized < color_norm_min:
                color_normalized = color_norm_min
            elif color_normalized < color_norm_min:
                color_normalized = color_norm_min

            color_normalized = (color_normalized - color_norm_min) / (color_norm_max - color_norm_min)
            if color_is_log:
                color_normalized = np.exp(color_normalized) / np.exp(1)

            if color_map_id == 0:
                # Divergent colormap
                rgb = color_map_divergent(color_normalized)
            else:
                # Cyclic colormap
                rgb = color_map_cyclic(color_normalized)

            # Clip before normalizing, needed for logarithmic normalization
            alpha_normalized = alpha_norm_values[i]
            if alpha_normalized < alpha_norm_min:
                alpha_normalized = alpha_norm_min
            elif alpha_normalized > alpha_norm_max:
                alpha_normalized = alpha_norm_max

            alpha_normalized = (alpha_normalized - alpha_norm_min) / (alpha_norm_max - alpha_norm_min)
            if alpha_is_log:
                alpha_normalized = np.exp(alpha_normalized) / np.exp(1)

            colors[i] = np.array([rgb[0], rgb[1], rgb[2], alpha_normalized])

        return colors

    def recalculate(self, wire, sampling_volume, field, progress_callback) -> bool:
        """
        Recalculates color and alpha values for field.

        @param wire: Wire
        @param sampling_volume: SamplingVolume
        @param field: Field
        @param progress_callback: Progress callback
        @return: True (currently non-interruptable)
        """
        Debug(self, ".recalculate()", color=Theme.SuccessColor)

        n = len(field.get_vectors())

        progress_callback(0)

        # Calculate color and alpha metric values
        color_norm_values, alpha_norm_values = self._norm_worker(
            self._color_preset["norm_id"],
            self._alpha_preset["norm_id"],
            field.get_vectors()
        )

        progress_callback(50)

        # Select color range
        if self._color_preset["is_angle"]:
            color_norm_min, color_norm_max = 0, 1
        else:
            color_norm_min, color_norm_max = min(color_norm_values), max(color_norm_values)

        # Select alpha range
        if self._alpha_preset["is_angle"]:
            alpha_norm_min, alpha_norm_max = 0, 1
        else:
            alpha_norm_min, alpha_norm_max = min(alpha_norm_values), max(alpha_norm_values)

        # Select color normalizer
        if self._color_preset["is_log"]:
            # Logarithmic normalization

            Assert_Dialog(not self._color_preset["is_angle"], "Logarithmic angles don't make any sense")

            # Adjust range for logarithm (out-of-range values will be clipped in the loop below)
            color_norm_min_ = max(color_norm_min, Metric.LogNormMinimum)    # avoiding ValueError: min must be positive
            color_norm_max_ = max(color_norm_min_, color_norm_max)          # avoiding ValueError: min must be <= max
        else:
            # Linear normalization
            color_norm_min_ = color_norm_min
            color_norm_max_ = color_norm_max

        # Select alpha normalizer
        if self._alpha_preset["is_log"]:
            # Logarithmic normalization

            Assert_Dialog(not self._alpha_preset["is_angle"], "Logarithmic angles don't make any sense")

            # Adjust range for logarithm (out-of-range values will be clipped in the loop below)
            alpha_norm_min_ = max(alpha_norm_min, Metric.LogNormMinimum)    # avoiding ValueError: min must be positive
            alpha_norm_max_ = max(alpha_norm_min_, alpha_norm_max)          # avoiding ValueError: min must be <= max
        else:
            # Linear normalization
            alpha_norm_min_ = alpha_norm_min
            alpha_norm_max_ = alpha_norm_max

        colors = np.zeros([n, 4])

        # Calculate final color values
        # Note: If using logarithmic scaling, out-of-range values (still exceeding [0...1] here) may be clipped
        colors = self._normalize_worker(
            self._color_preset["colormap"],
            self._color_preset["is_log"],
            color_norm_values,
            color_norm_min_,
            color_norm_max_,
            self._alpha_preset["is_log"],
            alpha_norm_values,
            alpha_norm_min_,
            alpha_norm_max_,
            colors
        )

        self._colors = colors

        self._limits = {
            "color_min": color_norm_min,
            "color_max": color_norm_max,
            "alpha_min": alpha_norm_min,
            "alpha_max": alpha_norm_max
        }

        progress_callback(100)

        return True

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @jit(nopython=True, parallel=True)
    def boost_colors(boost: float, direction: float, colors):
        """
        "Boosts" an array of color values.

        @param boost: Boost value
        @param direction: Boost direction
        @param colors: Colors (ordered list of 4-tuples)
        @return: Colors (ordered list of 4-tuples)
        """
        for i in prange(len(colors)):
            r = np.max(np.array([0.0, np.min(np.array([1.0, colors[i][0] + boost * direction]))]))
            g = np.max(np.array([0.0, np.min(np.array([1.0, colors[i][1] + boost * direction]))]))
            g = np.max(np.array([0.0, np.min(np.array([1.0, colors[i][1] + boost * direction]))]))
            b = np.max(np.array([0.0, np.min(np.array([1.0, colors[i][2] + boost * direction]))]))
            a = np.max(np.array([0.0, np.min(np.array([1.0, colors[i][3] + boost]))]))
            colors[i] = np.array([r, g, b, a])

        return colors
