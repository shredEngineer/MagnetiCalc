""" QCheckboxConfig module. """

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

from __future__ import annotations
from typing import Callable, Dict
from functools import partial
from PyQt5.QtWidgets import QAction, QMenu
from magneticalc.Debug import Debug


class QCheckboxConfig:
    """ QCheckboxConfig class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Initializes a manager for configuration bound checkbox actions.
        """
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.actions: Dict[str, Dict] = {}

    def add(self, label: str, key: str, on_changed: Callable) -> QAction:
        """
        Creates a checkbox action.
        The checkbox state is bound to the project configuration.

        @param label: Label
        @param key: Configuration key
        @param on_changed: Gets called when the checkbox state changed
        """
        action = QAction(label)
        action.setCheckable(True)
        action.triggered.connect(  # type: ignore
            partial(self.changed, key)
        )
        self.actions[key] = {"action": action, "on_changed": on_changed}
        action.setChecked(self.gui.project.get_bool(key))
        return action

    def changed(self, key: str) -> None:
        """
        Handles change of checkbox state.

        @param key: Configuration key
        """
        self.gui.project.set_bool(key, self.actions[key]["action"].isChecked())
        self.actions[key]["on_changed"]()

    def reload(self) -> None:
        """
        Reloads the configuration bound checkboxes.

        Note: This doesn't block the change signals.
        """
        for item in self.actions.items():
            key, dictionary = item
            dictionary["action"].setChecked(self.gui.project.get_bool(key))
