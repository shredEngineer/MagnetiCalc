""" Config module. """

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

from typing import Callable, Dict, List, Optional, Union
import os
import configparser
import numpy as np
from magneticalc.Debug import Debug
from magneticalc.Format import Format


class Config:
    """ Config class. """

    def __init__(self) -> None:
        """
        Initializes the configuration.
        """
        Debug(self, ": Init", init=True)
        self._parser: Optional[configparser.ConfigParser] = None
        self.filename: str = ""
        self.synced: bool = False
        self.on_changed: Optional[Callable] = None

    def load(self, filename: str, default_config: Dict) -> None:
        """
        Loads the configuration from file.

        @param filename: Filename
        @param default_config: Default config
        """
        self.filename = Format.absolute_filename(filename)
        Debug(self, f".load(): Loading file: {Format.filename_uri(self.filename)}")

        self._parser = configparser.ConfigParser()
        self._parser.read(self.filename)
        self._parser["DEFAULT"] = default_config

        if "User" not in self._parser:
            Debug(self, ".load(): Creating empty User section")
            self._parser["User"] = {}

        self.synced = True
        if self.on_changed is not None:
            self.on_changed()

        if not os.path.isfile(self.filename):
            Debug(self, f".load(): Creating file: {Format.filename_uri(self.filename)}")
            self.save()

    def save(self, filename: Optional[str] = None) -> None:
        """
        Saves the configuration to file.

        @param filename: Filename (optional)
        """
        assert self._parser is not None, "Not initialized"

        if filename is not None:
            self.filename = Format.absolute_filename(filename)

        Debug(self, f".save(): Saving file: {Format.filename_uri(self.filename)}")

        with open(self.filename, "w") as file:
            self._parser.write(file)

        self.synced = True
        if self.on_changed is not None:
            self.on_changed()

    def close(self) -> None:
        """
        Closes the configuration.
        """
        assert self._parser is not None, "Not initialized"

        Debug(self, ".close()")
        self._parser = None
        self.filename = ""
        self.synced = False

    # ------------------------------------------------------------------------------------------------------------------

    def remove_key(self, key: str) -> None:
        """
        Removes a key from the configuration.

        @param key: Key
        """
        assert self._parser is not None, "Not initialized"

        if not self._parser.remove_option("User", key):
            Debug(self, f".remove_key({key}): ERROR: No such key", error=True)

    # ------------------------------------------------------------------------------------------------------------------

    def set_get_str(self, key: str, value: str) -> str:
        """
        If value is not None, writes and returns key-value; otherwise (if value is None), reads and returns key-value.

        @param key: Key
        @param value: Value
        """
        if value is None:
            return self.get_str(key)
        else:
            self.set_str(key, value)
            return value

    def set_str(self, key: str, value: str) -> None:
        """
        Writes a configuration value. Key must be in "Default" section and may be overridden in "User" section.

        @param key: Key
        @param value: Value
        """
        assert self._parser is not None, "Not initialized"

        self._parser.set("User", key, value)
        self.synced = False
        if self.on_changed is not None:
            self.on_changed()

    def get_str(self, key: str) -> str:
        """
        Reads a configuration value. Key must be in "Default" section and may be overridden in "User" section.

        @param key: Key
        @return: Value
        """
        assert self._parser is not None, "Not initialized"

        value = self._parser.get("User", key)
        return value

    # ------------------------------------------------------------------------------------------------------------------

    def set_get_bool(self, key: str, value: bool) -> bool:
        """
        If value is not None, writes and returns key-value; otherwise (if value is None), reads and returns key-value.

        @param key: Key
        @param value: Value
        """
        if value is None:
            return self.get_bool(key)
        else:
            self.set_bool(key, value)
            return value

    def set_bool(self, key: str, value: bool) -> None:
        """
        Sets boolean value, convert to string.

        @param key: Key
        @param value: Value
        """
        self.set_str(key, "True" if value else "False")

    def get_bool(self, key: str) -> bool:
        """
        Gets boolean value, convert from string.

        @param key: Key
        @return: Value
        """
        return self.get_str(key) == "True"

    # ------------------------------------------------------------------------------------------------------------------

    def set_get_int(self, key: str, value: int) -> int:
        """
        If value is not None, writes and returns key-value; otherwise (if value is None), reads and returns key-value.

        @param key: Key
        @param value: Value
        """
        if value is None:
            return self.get_int(key)
        else:
            self.set_int(key, value)
            return value

    def set_int(self, key: str, value: int) -> None:
        """
        Sets integer value, convert to string.

        @param key: Key
        @param value: Value
        """
        self.set_str(key, str(int(value)))

    def get_int(self, key: str) -> int:
        """
        Gets integer value, convert from string.

        @param key: Key
        @return: Value
        """
        return int(self.get_str(key))

    # ------------------------------------------------------------------------------------------------------------------

    def set_get_float(self, key: str, value: float) -> float:
        """
        If value is not None, writes and returns key-value; otherwise (if value is None), reads and returns key-value.

        @param key: Key
        @param value: Value
        """
        if value is None:
            return self.get_float(key)
        else:
            self.set_float(key, value)
            return value

    def set_float(self, key: str, value: float) -> None:
        """
        Sets float value, convert to string.

        @param key: Key
        @param value: Value
        """
        self.set_str(key, Format.float_to_str(value))

    def get_float(self, key: str) -> float:
        """
        Gets float value, convert from string.

        @param key: Key
        @return: Value
        """
        return float(self.get_str(key))

    # ------------------------------------------------------------------------------------------------------------------

    def set_get_point(
            self,
            key: str,
            value: Union[np.ndarray, List[float]]
    ) -> Union[np.ndarray, List[float]]:
        """
        If value is not None, writes and returns key-value; otherwise (if value is None), reads and returns key-value.

        @param key: Key
        @param value: Value
        """
        if value is None:
            return self.get_point(key)
        else:
            self.set_point(key, value)
            return value

    def set_point(self, key: str, value: Union[np.ndarray, List[float]]) -> None:
        """
        Sets a single 3D point, convert to string.

        @param key: Key
        @param value: Single 3D point
        """
        self.set_str(key, Format.point_to_str(value))

    def get_point(self, key: str) -> List[float]:
        """
        Gets a single 3D point, convert from string.

        @param key: Key
        @return: Single 3D point
        """
        return Format.str_to_point(self.get_str(key))

    # ------------------------------------------------------------------------------------------------------------------

    def set_get_points(
            self,
            key: str,
            value: Union[np.ndarray, List[List[float]]]
    ) -> Union[np.ndarray, List[List[float]]]:
        """
        If value is not None, writes and returns key-value; otherwise (if value is None), reads and returns key-value.

        @param key: Key
        @param value: Value
        """
        if value is None:
            return self.get_points(key)
        else:
            self.set_points(key, value)
            return value

    def set_points(self, key: str, value: Union[np.ndarray, List[List[float]]]) -> None:
        """
        Sets list of 3D points, convert to string.

        @param key: Key
        @param value: List of 3D points
        """
        self.set_str(key, Format.points_to_str(value))

    def get_points(self, key: str) -> List[List[float]]:
        """
        Gets list of 3D points, convert from string.

        @param key: Key
        @return: List of 3D points
        """
        return Format.str_to_points(self.get_str(key))

    # ------------------------------------------------------------------------------------------------------------------

    def set_get_dict(self, prefix: str, suffix: str, types: Dict, values: Optional[Dict]) -> Dict:
        """
        If "values" is None, reads and returns all key-values in "types".
        Note: The actual keys saved in the configuration file are prefixed with "prefix", and suffixed with "suffix".

        If "values" is not None, writes and returns all key-values in "types".
        Note: In this case, "values" must have the same keys as "types".

        @param prefix: Prefix
        @param suffix: Suffix
        @param types: Key:Type (Dictionary)
        @param values: Key:Value (Dictionary)
        """
        if values is None:
            result = {}
            for _key, _type in types.items():
                result[_key] = self.get_generic(prefix + _key + suffix, _type)
            return result
        else:
            for _key, _type in types.items():
                self.set_generic(prefix + _key + suffix, _type, values[_key])
            return values

    def get_generic(
            self,
            _key: str,
            _type: str
    ) -> Union[str, bool, int, float, np.ndarray, List[float], List[List[float]]]:
        """
        Gets some "_key"-"_value" of data type "_type".

        @param _key: Key
        @param _type: Data type
        @return: Data (type determined by "_type")
        """
        set_func = {
            "bool"  : self.get_bool,
            "float" : self.get_float,
            "int"   : self.get_int,
            "point" : self.get_point,
            "points": self.get_points,
            "str"   : self.get_str
        }

        if _type in set_func:
            return set_func[_type](_key)
        else:
            raise TypeError("Invalid type")

    def set_generic(
            self,
            _key: str,
            _type: str,
            _value: Union[str, bool, int, float, np.ndarray, List[float], List[List[float]]]
    ) -> None:
        """
        Sets some "_key"-"_value" of data type "_type".

        @param _key: Key
        @param _type: Data type
        @param _value: Data (type determined by "_type")
        """
        set_func = {
            "bool"  : self.set_bool,
            "float" : self.set_float,
            "int"   : self.set_int,
            "point" : self.set_point,
            "points": self.set_points,
            "str"   : self.set_str
        }

        if _type in set_func:
            set_func[_type](_key, _value)
        else:
            raise TypeError("Invalid type")
