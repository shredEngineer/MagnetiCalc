""" Config_Group module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm <anfrage@paulwilhelm.de>
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
from typing import Callable
from collections.abc import MutableMapping


class Config_Group(MutableMapping):
    """ Config_Group class. """

    def __init__(
            self,
            config_collection: Config_Collection,  # type: ignore
            group_index: int,
            on_changed: Callable
    ) -> None:
        """
        Initializes a config group (dictionary).
        This group is liked to its collection, so any access to it is mapped directly to the configuration.

        @param config_collection: Config_Collection
        @param group_index: Group index
        @param on_changed: Gets called when any data in the group changed
        """
        self.collection = config_collection
        self.group_index = group_index
        self.on_changed = on_changed

    def set(self, data):
        self.collection.write_group_data(self.group_index, data)
        if self.on_changed is not None:
            self.on_changed()

    def __getitem__(self, key):
        return self.collection.read_group_data(self.group_index)[self._keytransform(key)]

    def __setitem__(self, key, value):
        self.set({self._keytransform(key): value})
        if self.on_changed is not None:
            self.on_changed()

    def __delitem__(self, key):
        raise NotImplementedError("Can't delete item from Config_Group")

    def __iter__(self):
        return iter(self.collection.read_group_data(self.group_index))

    def __len__(self):
        return len(self.collection.read_group_data(self.group_index))

    # noinspection PyMethodMayBeStatic
    def _keytransform(self, key):
        return key
