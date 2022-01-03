""" Menu module. """

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

from __future__ import annotations
from functools import partial
import webbrowser
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QActionGroup
from magneticalc.About_Dialog import About_Dialog
from magneticalc.Backend_Types import BACKEND_JIT, BACKEND_CUDA
from magneticalc.Backend_CUDA import Backend_CUDA
from magneticalc.CheckForUpdates_Dialog import CheckForUpdates_Dialog
from magneticalc.Debug import Debug
from magneticalc.ExportContainer_Dialog import ExportContainer_Dialog
from magneticalc.Usage_Dialog import Usage_Dialog
from magneticalc.Wire_Presets import Wire_Presets
from magneticalc.Version import __URL__

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class Menu:
    """ Menu class. """

    # List of available backends
    Backends_Available_List = {
        "Backend: JIT"          : True,
        "Backend: JIT + CUDA"   : Backend_CUDA.is_available()
    }

    def __init__(self, gui: GUI) -> None:
        """
        Creates the menu bar.

        @param gui: GUI
        """
        Debug(self, ": Init")
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
        file_menu.addAction(
            qta.icon("fa.folder"),
            "&Export Container …",
            lambda: ExportContainer_Dialog(self.gui).show(),
            Qt.CTRL + Qt.Key_E
        )
        file_menu.addSeparator()
        file_menu.addAction(qta.icon("fa.window-close"), "&Quit", self.gui.confirm_close, Qt.CTRL + Qt.Key_Q)
        self.gui.menuBar().addMenu(file_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Wire menu
        wire_menu = QMenu("&Wire", self.gui)

        load_preset_menu = QMenu("Load &Preset", self.gui)
        load_preset_menu.setIcon(qta.icon("mdi.vector-square"))
        for preset in Wire_Presets.List:
            action = QAction(preset["id"], wire_menu)
            action.setIcon(qta.icon("mdi.vector-square"))
            # noinspection PyUnresolvedReferences
            action.triggered.connect(
                partial(
                    self.gui.sidebar_left.wire_widget.set_wire,
                    points=preset["points"],
                    stretch=[1.0, 1.0, 1.0],
                    rotational_symmetry={
                        "count" : 1,
                        "radius": 0,
                        "axis"  : 2,
                        "offset": 0
                    }
                )
            )
            load_preset_menu.addAction(action)

        wire_menu.addMenu(load_preset_menu)
        wire_menu.addSeparator()

        self.import_wire_action = QAction("&Import TXT …")
        self.import_wire_action.setIcon(qta.icon("fa.folder"))
        # noinspection PyUnresolvedReferences
        self.import_wire_action.triggered.connect(self.gui.import_wire)
        wire_menu.addAction(self.import_wire_action)

        self.export_wire_action = QAction("&Export TXT …")
        self.export_wire_action.setIcon(qta.icon("fa.save"))
        self.export_wire_action.setEnabled(False)
        # noinspection PyUnresolvedReferences
        self.export_wire_action.triggered.connect(self.gui.export_wire)
        wire_menu.addAction(self.export_wire_action)

        self.gui.menuBar().addMenu(wire_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # View menu
        view_menu = QMenu("&View", self.gui)
        self.add_config_bound_checkbox("Show Wire Segments", "show_wire_segments", view_menu, self.gui.redraw)
        self.add_config_bound_checkbox("Show Wire Points", "show_wire_points", view_menu, self.gui.redraw)
        view_menu.addSeparator()
        self.add_config_bound_checkbox("Show Colored Labels", "show_colored_labels", view_menu, self.gui.redraw)
        self.add_config_bound_checkbox(
            "Show Gauss (Gs) instead of Tesla (T)", "show_gauss", view_menu, self.on_show_gauss_changed
        )
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
        for i, item in enumerate(self.Backends_Available_List.items()):
            name, enabled = item
            action = QAction(name)
            self.backend_actions.append(action)
            action.setCheckable(True)
            action.setEnabled(enabled)
            # noinspection PyUnresolvedReferences
            action.changed.connect(partial(self.on_backend_changed, i))
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
            qta.icon("fa.newspaper-o"), "&Check for Updates …", lambda: CheckForUpdates_Dialog().show(),
            Qt.Key_F4
        )
        help_menu.addAction(qta.icon("fa.github"), "&GitHub Repository …", partial(webbrowser.open, __URL__))
        help_menu.addSeparator()
        help_menu.addAction(qta.icon("fa.coffee"), "&About …", lambda: About_Dialog().show())
        self.gui.menuBar().addMenu(help_menu)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.reinitialize()

    def reinitialize(self) -> None:
        """
        Re-initializes the menu.
        """
        Debug(self, ".reinitialize()")

        self.gui.blockSignals(True)

        # Default to JIT backend if CUDA backend is selected but not available
        if self.gui.config.get_int("backend_type") == BACKEND_CUDA:
            if not Backend_CUDA.is_available():
                self.gui.config.set_int("backend_type", BACKEND_JIT)

        for i, name in enumerate(self.Backends_Available_List):
            self.backend_actions[i].setChecked(self.gui.config.get_int("backend_type") == i)

        self.reinitialize_config_bound_checkboxes()

        self.gui.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def on_show_gauss_changed(self) -> None:
        """
        Gets called when the "Show Gauss instead of Tesla" option changed.
        """
        self.gui.sidebar_right.metric_widget.update_labels()
        self.gui.vispy_canvas.delete_field_labels()
        self.gui.redraw()

    # ------------------------------------------------------------------------------------------------------------------

    def on_backend_changed(self, index) -> None:
        """
        Gets called when the backend changed.

        @param index: Backend list index
        """
        if self.gui.signalsBlocked():
            return

        if self.backend_actions[index].isChecked():
            self.gui.config.set_int("backend_type", index)
            self.gui.sidebar_right.field_widget.set_field()

    # ------------------------------------------------------------------------------------------------------------------

    def add_config_bound_checkbox(self, label: str, key: str, menu, callback) -> None:
        """
        Creates a checkbox inside some menu. Checkbox state is bound to configuration.

        @param label: Checkbox label
        @param key: Configuration key
        @param menu: Menu
        @param callback:
        """
        checkbox = QAction(label, menu)
        checkbox.setCheckable(True)
        # noinspection PyUnresolvedReferences
        checkbox.triggered.connect(partial(self.config_bound_checkbox_changed, key))
        self.config_bound_checkboxes[key] = {"checkbox": checkbox, "callback_final": callback}
        checkbox.setChecked(self.gui.config.get_bool(key))
        menu.addAction(checkbox)

    def config_bound_checkbox_changed(self, key: str) -> None:
        """
        Handles change of checkbox state.

        @param key: Configuration key
        """
        self.gui.config.set_bool(key, self.config_bound_checkboxes[key]["checkbox"].isChecked())
        self.config_bound_checkboxes[key]["callback_final"]()

    def reinitialize_config_bound_checkboxes(self) -> None:
        """
        Re-initializes the configuration bound checkboxes.

        Note: This doesn't block the change signals.
        """
        for item in self.config_bound_checkboxes.items():
            key, dictionary = item
            dictionary["checkbox"].setChecked(self.gui.config.get_bool(key))

    # ------------------------------------------------------------------------------------------------------------------

    def update_wire_menu(self) -> None:
        """
        Updates the wire menu.
        """
        Debug(self, ".update_wire_menu()")

        self.export_wire_action.setEnabled(self.gui.model.wire.is_valid())
