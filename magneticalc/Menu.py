""" Menu module. """

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

import qtawesome as qta
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup
from magneticalc.About_Dialog import About_Dialog
from magneticalc.BiotSavart_CUDA import BiotSavart_CUDA
from magneticalc.Debug import Debug
from magneticalc.Usage_Dialog import Usage_Dialog
from magneticalc.Wire_Presets import Wire_Presets


class Menu:
    """ Menu class. """

    # List of available backends
    Backends_List = {
        "Backend: JIT": True,
        "Backend: JIT + CUDA": BiotSavart_CUDA.is_available()
    }

    def __init__(self, gui):
        """
        Creates the menu bar.

        @param gui: GUI
        """
        self.gui = gui

        # List of checkboxes that are bound to configuration
        self.config_bound_checkboxes = {}

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # File menu
        file_menu = QMenu("&File", self.gui)
        file_menu.addAction(qta.icon("fa.folder"), "&Open File …", self.gui.file_open, Qt.CTRL + Qt.Key_O)
        file_menu.addAction(qta.icon("fa.save"), "&Save File", self.gui.file_save, Qt.CTRL + Qt.Key_S)
        file_menu.addAction(
            qta.icon("fa.save"),
            "Save File &As …",
            self.gui.file_save_as,
            Qt.CTRL + Qt.SHIFT + Qt.Key_S
        )
        file_menu.addSeparator()
        file_menu.addAction(qta.icon("fa.picture-o"), "Save &Image …", self.gui.file_save_image, Qt.CTRL + Qt.Key_I)
        file_menu.addSeparator()
        file_menu.addAction(qta.icon("fa.window-close"), "&Quit", self.gui.close, Qt.CTRL + Qt.Key_Q)
        self.gui.menuBar().addMenu(file_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Wire menu
        wire_menu = QMenu("&Load Wire Preset", self.gui)
        for preset in Wire_Presets.List:
            action = QAction(preset["id"], wire_menu)
            action.setIcon(qta.icon("mdi.vector-square"))
            action.triggered.connect(
                partial(self.gui.sidebar_left.wire_widget.set_wire, points=preset["points"])
            )
            wire_menu.addAction(action)
        self.gui.menuBar().addMenu(wire_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # View menu
        view_menu = QMenu("&View", self.gui)
        self.add_config_bound_checkbox("Show Wire Segments", "show_wire_segments", view_menu, self.gui.redraw)
        self.add_config_bound_checkbox("Show Wire Points", "show_wire_points", view_menu, self.gui.redraw)
        view_menu.addSeparator()
        self.add_config_bound_checkbox("Show Colored Labels", "show_colored_labels", view_menu, self.gui.redraw)
        view_menu.addSeparator()
        self.add_config_bound_checkbox("Show Coordinate System", "show_coordinate_system", view_menu, self.gui.redraw)
        self.add_config_bound_checkbox("Show Perspective Info", "show_perspective_info", view_menu, self.gui.redraw)
        view_menu.addSeparator()
        self.add_config_bound_checkbox("Dark Background", "dark_background", view_menu, self.gui.redraw)
        self.gui.menuBar().addMenu(view_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Options menu
        options_menu = QMenu("&Options", self.gui)
        self.options_backend_group = QActionGroup(self.gui)
        self.options_backend_group.setExclusive(True)
        self.gui.blockSignals(True)
        self.backend_actions = []
        for i, item in enumerate(self.Backends_List.items()):
            name, enabled = item
            action = QAction(name)
            self.backend_actions.append(action)
            action.setCheckable(True)
            action.setEnabled(enabled)
            action.changed.connect(partial(self.on_backend_changed, i))
            self.options_backend_group.addAction(action)
            options_menu.addAction(action)
        self.gui.blockSignals(False)
        self.gui.menuBar().addMenu(options_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Help menu
        help_menu = QMenu("&Help", self.gui)
        help_menu.addAction(qta.icon("fa.info"), "&Usage", lambda: Usage_Dialog().show(), Qt.Key_F1)
        help_menu.addSeparator()
        help_menu.addAction(qta.icon("fa.coffee"), "&About", lambda: About_Dialog().show())
        self.gui.menuBar().addMenu(help_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self):
        """
        Re-initializes the menu.
        """
        Debug(self, ".reinitialize()")

        self.gui.blockSignals(True)

        # Default to JIT backend if CUDA backend is selected but not available
        if self.gui.config.get_int("backend") == 1:
            if not BiotSavart_CUDA.is_available():
                self.gui.config.set_int("backend", 0)

        for i, name in enumerate(self.Backends_List):
            self.backend_actions[i].setChecked(self.gui.config.get_int("backend") == i)

        self.reinitialize_config_bound_checkboxes()

        self.gui.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def on_backend_changed(self, index):
        """
        Gets called when the backend changed.

        @param index: Backend list index
        """
        if self.gui.signalsBlocked():
            return

        if self.backend_actions[index].isChecked():
            self.gui.config.set_int("backend", index)
            self.gui.sidebar_right.field_widget.set_field()

    # ------------------------------------------------------------------------------------------------------------------

    def add_config_bound_checkbox(self, label: str, key: str, menu, callback):
        """
        Creates a checkbox inside some menu. Checkbox state is bound to configuration.

        @param label: Checkbox label
        @param key: Configuration key
        @param menu: Menu
        @param callback:
        """
        checkbox = QAction(label, menu)
        checkbox.setCheckable(True)
        checkbox.triggered.connect(partial(self.config_bound_checkbox_changed, key))
        self.config_bound_checkboxes[key] = {"checkbox": checkbox, "callback_final": callback}
        checkbox.setChecked(self.gui.config.get_bool(key))
        menu.addAction(checkbox)

    def config_bound_checkbox_changed(self, key: str):
        """
        Handles change of checkbox state.

        @param key: Configuration key
        """
        self.gui.config.set_bool(key, self.config_bound_checkboxes[key]["checkbox"].isChecked())
        self.config_bound_checkboxes[key]["callback_final"]()

    def reinitialize_config_bound_checkboxes(self):
        """
        Re-initializes the configuration bound checkboxes.

        Note: This doesn't block the change signals.
        """
        for item in self.config_bound_checkboxes.items():
            key, dictionary = item
            dictionary["checkbox"].setChecked(self.gui.config.get_bool(key))
