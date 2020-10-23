""" Config module. """

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

import os
import configparser
from magneticalc.Debug import Debug
from magneticalc.Wire import Wire


class Config:
    """ Config class. """

    # Configuration filename
    Filename = "MagnetiCalc.ini"

    # Enable to instantly save every change to file (useful for debugging)
    InstantSave = True

    # Enable to additionally debug read access to configuration
    DebugGetters = False

    # Default wire preset
    DefaultWirePreset = "Compensated Double Loop (centered)"

    # Default configuration
    Default = {
        "window_width"                  : "1500",
        "window_height"                 : "1000",
        "auto_calculation"              : "True",
        "num_cores"                     : "0",
        "wire_points_base"              : None,  # Will be set in __init__
        "wire_stretch"                  : "1.0, 1.0, 1.0",
        "wire_slicer_limit"             : "0.1",
        "wire_dc"                       : "1.0",
        "rotational_symmetry_count"     : "4",
        "rotational_symmetry_radius"    : "1.0",
        "rotational_symmetry_axis"      : "2",
        "sampling_volume_padding"       : "1, -2, 2",
        "sampling_volume_resolution"    : "8.0",
        "color_metric"                  : "Log Magnitude XZ",
        "alpha_metric"                  : "Log Magnitude",
        "field_point_scale"             : "1.0",
        "field_arrow_scale"             : "0.3",
        "field_boost"                   : "0.1",
        "show_wire_segments"            : "True",
        "show_wire_points"              : "True",
        "show_coordinate_system"        : "True",
        "show_perspective_info"         : "True",
        "dark_background"               : "True",
        "azimuth"                       : "0",
        "elevation"                     : "0",
        "scale_factor"                  : "6.5"
    }

    def __init__(self):
        """
        Loads configuration from file.
        """
        self.absolute_filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.Filename)

        Debug(self, ": file://" + self.absolute_filename.replace(" ", "%20"), force=True)

        self.Default["wire_points_base"] = Config.points_to_str(Wire.get_by_id(Config.DefaultWirePreset)["points"])

        self.config = configparser.ConfigParser()
        self.synced = False

        self.load()

    def close(self):
        """
        Finally auto-saves configuration to file.
        """
        Debug(self, ".close()")

        if not self.synced:
            self.save()

    def load(self):
        """
        Loads the configuration from file.
        """
        Debug(self, ".load: " + self.absolute_filename)

        self.config.read(self.absolute_filename)
        self.set_defaults()
        self.synced = True

    def set_defaults(self):
        """
        Sets the default key-value pairs. Creates empty "User" section if not present.
        """
        self.config["DEFAULT"] = Config.Default

        if "User" not in self.config:
            Debug(self, ".set_defaults(): Creating empty User section")
            self.config["User"] = {}

    def save(self):
        """
        Saves the configuration to file.
        """
        Debug(self, ".save()")

        with open(self.Filename, "w") as file:
            self.config.write(file)
        self.synced = True

    def get_bool(self, key):
        """
        Gets boolean value, convert from string.

        @param key: Key
        @return: Value
        """
        return self.get_str(key) == "True"

    def get_float(self, key):
        """
        Gets float value, convert from string.

        @param key: Key
        @return: Value
        """
        return float(self.get_str(key))

    def get_int(self, key):
        """
        Gets integer value, convert from string.

        @param key: Key
        @return: Value
        """
        return int(self.get_str(key))

    def get_points(self, key):
        """
        Gets list of 3D points, convert from string.

        @param key: Key
        @return: List of 3D points
        """
        return Config.str_to_points(self.get_str(key))

    def get_point(self, key):
        """
        Gets a single 3D point, convert from string.

        @param key: Key
        @return: Single 3D point
        """
        return Config.str_to_point(self.get_str(key))

    def get_str(self, key):
        """
        Reads a configuration value. Key must be in "Default" section and may be overridden in "User" section.

        @param key: Key (string)
        @return: Value (string)
        """
        if self.DebugGetters:
            Debug(self, f".get_str({key})")

        value = self.config.get("User", key)
        return value

    def set_bool(self, key, value):
        """
        Sets boolean value, convert to string.

        @param key: Key
        @param value: Value
        """
        self.set_str(key, "True" if value else "False")

    def set_float(self, key, value):
        """
        Sets float value, convert to string.

        @param key: Key
        @param value: Value
        """
        self.set_str(key, f"{float(value):.3f}")

    def set_int(self, key, value):
        """
        Sets integer value, convert to string.

        @param key: Key
        @param value: Value
        """
        self.set_str(key, str(int(value)))

    def set_points(self, key, value):
        """
        Sets list of 3D points, convert to string.

        @param key: Key
        @param value: List of 3D points
        """
        self.set_str(key, Config.points_to_str(value))

    def set_point(self, key, value):
        """
        Sets a single 3D point, convert to string.

        @param key: Key
        @param value: Single 3D point
        """
        self.set_str(key, Config.point_to_str(value))

    def set_str(self, key, value):
        """
        Writes a configuration value. Key must be in "Default" section and may be overridden in "User" section.

        @param key: Key (string)
        @param value: Value (string)
        """
        Debug(self, f".set_str({key}, {value})")

        self.config.set("User", key, value)
        self.synced = False

        if self.InstantSave:
            self.save()

    def set_get_bool(self, key, value):
        """
        If value is not None, writes and returns key-value; Otherwise (if value is None), reads and returns key-value.

        @param key: Key (string)
        @param value: Value (bool) or None
        """
        if value is None:
            return self.get_bool(key)
        else:
            self.set_bool(key, value)
            return value

    def set_get_float(self, key, value):
        """
        If value is not None, writes and returns key-value; Otherwise (if value is None), reads and returns key-value.

        @param key: Key (string)
        @param value: Value (float) or None
        """
        if value is None:
            return self.get_float(key)
        else:
            self.set_float(key, value)
            return value

    def set_get_int(self, key, value):
        """
        If value is not None, writes and returns key-value; Otherwise (if value is None), reads and returns key-value.

        @param key: Key (string)
        @param value: Value (int) or None
        """
        if value is None:
            return self.get_int(key)
        else:
            self.set_int(key, value)
            return value

    def set_get_points(self, key, value):
        """
        If value is not None, writes and returns key-value; Otherwise (if value is None), reads and returns key-value.

        @param key: Key (string)
        @param value: Value (string) or None
        """
        if value is None:
            return self.get_points(key)
        else:
            self.set_points(key, value)
            return value

    def set_get_point(self, key, value):
        """
        If value is not None, writes and returns key-value; Otherwise (if value is None), reads and returns key-value.

        @param key: Key (string)
        @param value: Value (string) or None
        """
        if value is None:
            return self.get_point(key)
        else:
            self.set_point(key, value)
            return value

    def set_get_str(self, key, value):
        """
        If value is not None, writes and returns key-value; Otherwise (if value is None), reads and returns key-value.

        @param key: Key (string)
        @param value: Value (string) or None
        """
        if value is None:
            return self.get_str(key)
        else:
            self.set_str(key, value)
            return value

    @staticmethod
    def point_to_str(point):
        """
        Converts a single 3D point to string.

        @param point: Single 3D point
        @return: String
        """
        return f"{point[0]:+0.03f}, {point[1]:+0.03f}, {point[2]:+0.03f}"

    @staticmethod
    def points_to_str(points):
        """
        Converts list of 3D points to string.

        @param points: List of 3D points
        @return: String
        """
        return "; ".join([Config.point_to_str(point) for point in points])

    @staticmethod
    def str_to_point(str_point):
        """
        Converts string to single 3D point.

        @param str_point: String
        @return: Single 3D point
        """
        return [float(coord) for coord in str_point.split(",")]

    @staticmethod
    def str_to_points(str_points):
        """
        Converts string to list of 3D points.

        @param str_points: String
        @return: List of 3D points
        """
        return [Config.str_to_point(str_point) for str_point in str_points.split(";")]
