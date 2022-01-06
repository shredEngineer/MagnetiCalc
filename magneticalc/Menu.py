""" Menu module. """

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
import webbrowser
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup
from magneticalc.About_Dialog import About_Dialog
from magneticalc.Backend_Types import Backend_Types_Available, backend_type_to_name
from magneticalc.CheckForUpdates_Dialog import CheckForUpdates_Dialog
from magneticalc.Debug import Debug
from magneticalc.File_Menu import File_Menu
from magneticalc.Usage_Dialog import Usage_Dialog
from magneticalc.Version import __URL__
from magneticalc.View_Menu import View_Menu
from magneticalc.Wire_Menu import Wire_Menu


class Menu:
    """ Menu class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ) -> None:
        """
        Creates the menu bar.

        @param gui: GUI
        """
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.file_menu = File_Menu(self.gui)
        self.wire_menu = Wire_Menu(self.gui)
        self.view_menu = View_Menu(self.gui)

        self.gui.menuBar().addMenu(self.file_menu)
        self.gui.menuBar().addMenu(self.wire_menu)
        self.gui.menuBar().addMenu(self.view_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Options menu
        options_menu = QMenu("&Options", self.gui)
        self.options_backend_group = QActionGroup(self.gui)
        self.options_backend_group.setExclusive(True)
        self.gui.blockSignals(True)
        self.backend_actions = []
        for i, item in enumerate(Backend_Types_Available.items()):
            backend_type, available = item
            action = QAction("Backend: " + backend_type_to_name(backend_type))
            self.backend_actions.append(action)
            action.setCheckable(True)
            action.setEnabled(available)
            action.changed.connect(  # type: ignore
                partial(self.on_backend_changed, i)
            )
            self.options_backend_group.addAction(action)
            options_menu.addAction(action)
        self.gui.blockSignals(False)
        self.gui.menuBar().addMenu(options_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Help menu
        help_menu = QMenu("&Help", self.gui)
        help_menu.addAction(qta.icon("fa.info"), "&Usage …", lambda: Usage_Dialog().show(), Qt.Key_F1)
        help_menu.addSeparator()
        help_menu.addAction(
            qta.icon("fa.newspaper-o"), "&Check for Updates …", lambda: CheckForUpdates_Dialog().show()
        )
        help_menu.addAction(
            qta.icon("fa.github"),
            "&GitHub Repository …",
            partial(webbrowser.open, __URL__)  # type: ignore
        )
        help_menu.addSeparator()
        help_menu.addAction(qta.icon("fa.coffee"), "&About …", lambda: About_Dialog().show())
        self.gui.menuBar().addMenu(help_menu)

    def reload(self) -> None:
        """
        Reloads the menu.
        """
        Debug(self, ".reload()", refresh=True)

        self.gui.blockSignals(True)

        # Reload the options menu state
        for i, item in enumerate(Backend_Types_Available.items()):
            backend_type, enabled = item
            self.backend_actions[i].setChecked(backend_type == self.gui.project.get_int("backend_type"))

        self.gui.blockSignals(False)

        self.update()

    def update(self) -> None:
        """
        Updates all menus.
        """
        Debug(self, ".update()", refresh=True)
        self.file_menu.update()
        self.wire_menu.update()
        self.view_menu.update()

    # ------------------------------------------------------------------------------------------------------------------

    def on_backend_changed(self, index) -> None:
        """
        Gets called when the backend changed.

        @param index: Backend list index
        """
        if self.gui.signalsBlocked():
            return

        if self.backend_actions[index].isChecked():
            self.gui.project.set_int("backend_type", index)
            self.gui.sidebar_right.field_widget.set_field()
