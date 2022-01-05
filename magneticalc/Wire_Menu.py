""" Wire_Menu module. """

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
import qtawesome as qta
from PyQt5.QtWidgets import QMenu, QFileDialog, QAction
from magneticalc.QSaveAction import QSaveAction
from magneticalc import API
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Debug import Debug
from magneticalc.Wire_Presets import Wire_Presets


class Wire_Menu(QMenu):
    """ Wire_Menu class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ):
        QMenu.__init__(self, "&Wire")
        Debug(self, ": Init", init=True)
        self.gui = gui

        load_preset_menu = QMenu("Load &Preset", self.gui)
        load_preset_menu.setIcon(qta.icon("mdi.vector-square"))
        for preset in Wire_Presets.List:
            action = QAction(qta.icon("mdi.vector-square"), preset["id"], self)
            action.triggered.connect(  # type: ignore
                partial(
                    self.gui.sidebar_left.wire_widget.set_wire,
                    _points_=preset["points"],
                    _stretch_=[1.0, 1.0, 1.0],
                    _rotational_symmetry_={
                        "count" : 1,
                        "radius": 0,
                        "axis"  : 2,
                        "offset": 0
                    }
                )
            )
            load_preset_menu.addAction(action)
        self.addMenu(load_preset_menu)

        self.addSeparator()

        self.import_wire_action = QAction(qta.icon("fa.folder"), "&Import TXT …")
        self.import_wire_action.triggered.connect(  # type: ignore
            self.wire_import
        )
        self.addAction(self.import_wire_action)

        self.export_wire_action = QAction(qta.icon("fa.save"), "&Export TXT …")
        self.export_wire_action.triggered.connect(  # type: ignore
            self.wire_export
        )
        self.addAction(self.export_wire_action)

        self.update()

    def update(self):
        """
        Updates the menu.
        """
        Debug(self, ".update()", refresh=True)
        self.export_wire_action.setEnabled(self.gui.model.wire.valid)

    # ------------------------------------------------------------------------------------------------------------------

    def wire_import(self) -> None:
        """
        Imports wire points from a TXT file.
        """
        Debug(self.gui, ".wire_import()")

        filename, _chosen_extension = QFileDialog.getOpenFileName(
            parent=self.gui,
            caption="Import Wire",
            filter="Text File (*.txt)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":

            points = API.import_wire(filename)
            self.gui.sidebar_left.wire_widget.set_wire(
                _points_=points,
                _stretch_=[1.0, 1.0, 1.0],
                _rotational_symmetry_={
                    "count": 1,
                    "radius": 0,
                    "axis": 2,
                    "offset": 0
                }
            )

    def wire_export(self) -> None:
        """
        Exports wire points to a TXT file.
        """
        Debug(self.gui, ".wire_export()")

        if not self.gui.model.wire.valid:
            Assert_Dialog(False, "Attempting to export invalid wire")
            return

        action = QSaveAction(
            self.gui,
            title="Export Wire",
            date=True,
            filename="MagnetiCalc_Wire",
            extension=".txt",
            _filter="Text File (*.txt)"
        )
        if action.filename:
            API.export_wire(action.filename, self.gui.model.wire.get_points_sliced())
