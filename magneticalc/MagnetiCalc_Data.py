""" MagnetiCalc_Data module. """

#  ISC License
#
#  Copyright (c) 2020–2021, Paul Wilhelm, M. Sc. <anfrage@paulwilhelm.de>
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
from typing import Dict, Tuple, List
from collections.abc import MutableMapping


class MagnetiCalc_Data(MutableMapping):
    """ MagnetiCalc_Data class. """

    def __init__(self, data: Dict) -> None:
        """
        Initializes MagnetiCalc_Data class.

        This object can be accessed like a dictionary to get the data from an HDF5 export.

        Moreover, it provides convenience functions for accessing reshaped or transformed copies of this data.

        @param data: Dictionary
        """
        self.data: Dict = {}
        self.update(data)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def get_wire(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Gets the wire points as three separate 1D arrays (raveled).

        @return: x, y, z
        """
        assert "wire_points" in self, "Sorry, there are no wire points in this data."
        wire_points = self["wire_points"]
        x, y, z = wire_points["x"], wire_points["y"], wire_points["z"]
        return x, y, z

    def get_wire_list(self) -> List:
        """
        Gets the wire points as a single list of 3D points (raveled).

        @return: List
        """
        return list(zip(self.get_wire()))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def get_current(self) -> float:
        """
        Gets the wire current.
        """
        assert "wire_current" in self, "Sorry, there is no wire current in this data."
        return self["wire_current"]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def get_dimension(self) -> Tuple[int, int, int]:
        """
        Gets the sampling volume dimension.

        @return: nx, ny, nz
        """
        fields = self._get_fields()
        return fields["nx"], fields["ny"], fields["nz"]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def get_axes(self, reduce: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Gets the sampling volume axes as three separate 1D arrays (raveled).

        @param reduce: Enable to reduce each raveled array to its minimal representation (axis ticks)
        @return: x, y, z
        """
        fields = self._get_fields()
        x, y, z = fields["x"], fields["y"], fields["z"]

        if reduce:
            x, y, z = np.array(sorted(list(set(x)))), np.array(sorted(list(set(y)))), np.array(sorted(list(set(z))))

        return x, y, z

    def get_axes_list(self, **kwargs) -> List:
        """
        Gets the sampling volume axes as a single list of 3D points (raveled).

        @return: List
        """
        return list(zip(self.get_axes(**kwargs)))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def get_field(self, field_type: str, as_3d: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Gets the field as three separate 1D arrays (raveled).

        @param field_type: Field type ("A" or "B")
        @param as_3d: Enable to transform each raveled 1D array into an unraveled 3D mesh (indexed by the minimal axes)
        """
        assert field_type in ["A", "B"], "Invalid field type"

        fields = self._get_fields()
        keys = [field_type + "_x", field_type + "_y", field_type + "_z"]
        assert all([key in fields for key in keys]), f"Sorry, there is no {field_type}-field in this data."
        field_x, field_y, field_z = [fields[key] for key in keys]

        if as_3d:
            shape_3d = self.get_dimension()
            field_x = np.reshape(field_x, shape_3d, order="F")
            field_y = np.reshape(field_y, shape_3d, order="F")
            field_z = np.reshape(field_z, shape_3d, order="F")

        return field_x, field_y, field_z

    def get_a_field(self, **kwargs) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Gets the A-field components as three separate 1D arrays (raveled).

        @param: A_x, A_y, A_z
        """
        return self.get_field("A", **kwargs)

    def get_a_field_list(self, **kwargs) -> List:
        """
        Gets the A-field components as a single list of 3D points (raveled).

        @param: List
        """
        return list(zip(self.get_a_field(**kwargs)))

    def get_b_field(self, **kwargs) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Gets the B-field components.

        @param: B_x, B_y, B_z
        """
        return self.get_field("B", **kwargs)

    def get_b_field_list(self, **kwargs) -> List:
        """
        Gets the B-field components as a single list of 3D points (raveled).

        @param: List
        """
        return list(zip(self.get_b_field(**kwargs)))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _get_fields(self) -> Dict:
        """
        Gets the raw "fields" dictionary from the data.

        @return: Dictionary
        """
        assert "fields" in self, "Sorry, there are no fields in this data."
        return self["fields"]

    # ------------------------------------------------------------------------------------------------------------------

    def __getitem__(self, key):
        return self.data[self._keytransform(key)]

    def __setitem__(self, key, value):
        self.data[self._keytransform(key)] = value

    def __delitem__(self, key):
        del self.data[self._keytransform(key)]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    # noinspection PyMethodMayBeStatic
    def _keytransform(self, key):
        return key
