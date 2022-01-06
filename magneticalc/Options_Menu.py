""" Options_Menu module. """

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
from functools import partial
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup
from magneticalc.Backend_Types import Backend_Types_Available, backend_type_to_name
from magneticalc.Debug import Debug


class Options_Menu(QMenu):
    """ Options_Menu class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ):
        QMenu.__init__(self, "&Options")
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.options_backend_group = QActionGroup(self.gui)
        self.options_backend_group.setExclusive(True)

        self.backend_actions = {}
        for backend_type, backend_available in Backend_Types_Available.items():
            self.backend_actions[backend_type] = QAction("Backend: " + backend_type_to_name(backend_type))
            self.backend_actions[backend_type].setEnabled(backend_available)
            self.backend_actions[backend_type].setCheckable(True)
            self.options_backend_group.addAction(self.backend_actions[backend_type])
            self.addAction(self.backend_actions[backend_type])
        for backend_type in Backend_Types_Available:
            self.backend_actions[backend_type].changed.connect(  # type: ignore
                partial(self.on_backend_changed, backend_type)
            )

    def update(self):
        """
        Updates the menu.
        """
        Debug(self, ".update()", refresh=True)
        self.gui.blockSignals(True)

        backend_type = self.gui.project.get_int("backend_type")
        for _backend_type in Backend_Types_Available:
            self.backend_actions[_backend_type].setChecked(backend_type == _backend_type)

        self.gui.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def on_backend_changed(self, backend_type: int) -> None:
        """
        Gets called when the backend changed.

        @param backend_type: Backend type
        """
        if self.gui.signalsBlocked():
            return

        if self.backend_actions[backend_type].isChecked():
            self.gui.project.set_int("backend_type", backend_type)
            self.gui.sidebar_right.field_widget.set_field()
