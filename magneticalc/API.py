""" API module. """

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

import h5py
import numpy as np
from typing import Dict, List, Union
from magneticalc.MagnetiCalc_Data import MagnetiCalc_Data


class API:
    """ API class. """

    @staticmethod
    def import_wire(filename: str) -> np.ndarray:
        """
        Imports wire points from a TXT file.

        @param filename: Filename
        @return: NumPy array of 3D points
        """
        data = np.loadtxt(filename)
        assert data.shape[1] == 3, "Expecting array of 3D points"
        return data

    @staticmethod
    def export_wire(filename: str, data: Union[List, np.ndarray]) -> None:
        """
        Exports wire points to a TXT file.

        @param filename: Filename
        @param data: NumPy array of 3D points
        """
        data = np.array(data)
        assert data.shape[1] == 3, "Expecting array of 3D points"
        # noinspection PyTypeChecker
        np.savetxt(filename, data)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def import_hdf5(filename: str) -> MagnetiCalc_Data:
        """
        Imports data from an HDF5 container.

        Opens an HDF5 file and converts every group and subgroup into a dictionary
        where the keys are the group keys and the items are the datasets.

        @param filename: Filename
        @return: MagnetiCalc_Data object (can be accessed like a dictionary)
        """
        hdf5_group = h5py.File(filename, "r")
        data = {}
        API._hdf5_group_to_dict(hdf5_group, data)
        hdf5_group.close()
        return MagnetiCalc_Data(data)

    @staticmethod
    def export_hdf5(filename: str, data: Union[Dict, MagnetiCalc_Data]) -> None:
        """
        Exports data to an HDF5 container.

        Takes a dictionary and writes an HDF5 file using keys as keys,
        and items as groups if they are dictionaries or as datasets otherwise.

        @param filename: Filename
        @param data: Dictionary or MagnetiCalc_Data object
        """
        hdf5_group = h5py.File(filename, "w")
        API._dict_to_hdf5_group(hdf5_group, data)
        hdf5_group.close()

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _dict_to_hdf5_group(hdf5_group: h5py.Group, dictionary: Dict) -> None:
        """
        Recursively transforms a dictionary into an HDF5 group (in-place).

        @param hdf5_group: HDF5 group
        @param dictionary: Dictionary
        """
        for key in dictionary.keys():
            if isinstance(dictionary[key], dict):
                group = hdf5_group.create_group(key)
                API._dict_to_hdf5_group(group, dictionary[key])
            else:
                hdf5_group[key] = dictionary[key]

    @staticmethod
    def _hdf5_group_to_dict(hdf5_group: h5py.Group, dictionary: Dict) -> None:
        """
        Recursively transforms an HDF5 group into a dictionary (in-place).

        @param hdf5_group: HDF5 group
        @param dictionary: Dictionary
        """
        for key in [key for key in hdf5_group]:
            if isinstance(hdf5_group[key], h5py.Dataset):
                dictionary[key] = hdf5_group[key][()]
            else:
                dictionary[key] = {}
                API._hdf5_group_to_dict(hdf5_group[key], dictionary[key])
