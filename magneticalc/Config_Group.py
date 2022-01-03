""" Config_Collection module. """

#  ISC License
#
#  Copyright (c) 2020–2021, Paul Wilhelm <anfrage@paulwilhelm.de>
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

from __future__ import annotations
from typing import Optional, List, Dict
from magneticalc.Assert_Dialog import Assert_Dialog

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class Config_Collection:
    """ Config_Collection class. """

    def __init__(self, gui: GUI, prefix: str, types: Dict, first_without_suffix: bool) -> None:
        """
        Initializes a config collection: A list of groups (dictionaries).

        Example for the SOMETHING collection, consisting of two groups _0 and _1, each with two keys FOO and BAR:
            SOMETHING_count = 2
            SOMETHING_FOO_0 = "1st value in 1st group"
            SOMETHING_BAR_0 = "2nd value in 1st group"
            SOMETHING_FOO_1 = "1st value in 2nd group"
            SOMETHING_BAR_1 = "2nd value in 2nd group"

        @param gui: GUI
        @param prefix: Prefix
        @param types: Key:Type (Dictionary)
        @param first_without_suffix: Enable to omit the suffix "_0" for the first group
        """
        self.gui = gui
        self.prefix = prefix
        self.types = types
        self.first_without_suffix = first_without_suffix

    def _get_suffix(self, group_index: int) -> str:
        """
        Gets the suffix for a given group index.

        @param group_index: Group index
        @return: String
        """
        return "" if group_index == 0 and self.first_without_suffix else f"_{group_index}"

    def get_count(self) -> int:
        """
        Gets the number of groups in the collection.

        @return: Number of groups in the collection
        """
        return self.gui.config.get_int(self.prefix + "count")

    def get_group(self, group_index: int) -> Dict:
        """
        Gets a group from the collection.

        @param group_index: Group index
        @return: Group (dictionary)
        """
        return self.gui.config.set_get_dict(
            prefix=self.prefix,
            suffix=self._get_suffix(group_index),
            types=self.types,
            values=None
        )

    def get_all_groups(self) -> List[Dict]:
        """
        Gets every group in the collection.

        @return: List of groups (dictionaries)
        """
        return [self.get_group(group_index) for group_index in range(self.get_count())]

    def add_group(self, values: Optional[Dict]) -> None:
        """
        Appends a group to the collection.

        @param values: Key:Value (Dictionary)
        """
        group_index = self.get_count()
        self.gui.config.set_int(self.prefix + "count", group_index + 1)
        self.gui.config.set_get_dict(
            prefix=self.prefix,
            suffix=self._get_suffix(group_index),
            types=self.types,
            values=values,
        )

    def del_group(self, group_index: int) -> None:
        """
        Deletes a group from the collection.

        @param group_index: Group index
        """
        Assert_Dialog(group_index < self.get_count(), "Attempting to delete non-existing group")

        # Make a copy of all groups
        groups = self.get_all_groups()

        # Delete the desired group from the copy
        del groups[group_index]

        # Delete all groups from the collection
        for i in range(self.get_count()):
            for key in self.types.keys():
                self.gui.config.remove_key(f"{self.prefix}{key}_{i}")

        # Clear the group count of the collection
        self.gui.config.set_int(self.prefix + "count", 0)

        # Recreate the groups of the collection (regenerate suffixes)
        for group in groups:
            self.add_group(group)

    def set(self, group_index: int, key: str, value) -> None:
        """
        Sets a value for some key in a group of the collection.

        @param group_index: Group index
        @param key: Key
        @param value: Value
        """
        _type = self.types.get(key)
        self.gui.config.set_generic(f"{self.prefix}{key}_{group_index}", _type, value)
