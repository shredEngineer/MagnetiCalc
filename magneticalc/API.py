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


class API:
    """ API class. """

    def __init__(self) -> None:
        """
        Initializes the API.
        """

    # ------------------------------------------------------------------------------------------------------------------

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

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def import_hdf5(filename: str) -> Dict:
        """
        Imports data from an HDF5 container.

        Opens an HDF5 file and converts every group and subgroup into a dictionary
        where the keys are the group keys and the items are the datasets.
        """
        hdf5_group = h5py.File(filename, "r")
        dictionary = {}
        API.hdf5_group_to_dict(hdf5_group, dictionary)
        hdf5_group.close()
        return dictionary

    @staticmethod
    def export_hdf5(filename: str, dictionary: Dict) -> None:
        """
        Exports data to an HDF5 container.

        Takes a dictionary and writes an HDF5 file using keys as keys,
        and items as groups if they are dictionaries or as datasets otherwise.
        """
        hdf5_group = h5py.File(filename, "w")
        API.dict_to_hdf5_group(hdf5_group, dictionary)
        hdf5_group.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def dict_to_hdf5_group(hdf5_group, dictionary) -> None:
        """
        Recursively transforms a dictionary into an HDF5 group (in-place).

        @param hdf5_group: HDF5 group
        @param dictionary: Dictionary
        """
        for key in dictionary.keys():
            if isinstance(dictionary[key], dict):
                group = hdf5_group.create_group(key)
                API.dict_to_hdf5_group(group, dictionary[key])
            else:
                hdf5_group[key] = dictionary[key]

    @staticmethod
    def hdf5_group_to_dict(hdf5_group, dictionary) -> None:
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
                API.hdf5_group_to_dict(hdf5_group[key], dictionary[key])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    @staticmethod
    def reshape_fields(dictionary: Dict) -> Dict:
        """
        Reshapes arrays obtained from import_hdf5() so that the axes are given
        by minimal one-dimensional arrays rather than raveled three-dimensional
        meshes. The fields are unraveled so that they are represented by
        three-dimensional arrays with axis0 -> x, axis1 -> y, and axis2 -> z.
        
        @param dictionary: Dictionary
        @return: Dictionary
        """
        axes = ["x", "y", "z"]
        new_dictionary = dictionary.copy()
        for key in axes:
            new_dictionary["fields"][key] = np.array(sorted(list(set(new_dictionary["fields"][key]))))
        new_shape = [len(new_dictionary["fields"][i]) for i in axes]
        for key in new_dictionary["fields"]:
            if not(key in axes):
                new_dictionary["fields"][key] = np.reshape(new_dictionary["fields"][key], new_shape, order="F")
        return new_dictionary
