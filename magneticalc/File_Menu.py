""" File_Menu module. """

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
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QFileDialog
from magneticalc.QSaveAction import QSaveAction
from magneticalc.Debug import Debug
from magneticalc.ExportContainer_Dialog import ExportContainer_Dialog


class File_Menu(QMenu):
    """ File_Menu class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ):
        QMenu.__init__(self, "&File")
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.addAction(
            qta.icon("fa.file"),
            "&New Project …",
            self.file_new,
            Qt.CTRL + Qt.Key_N
        )

        self.addAction(
            qta.icon("fa.folder"),
            "&Open Project …",
            self.file_open,
            Qt.CTRL + Qt.Key_O
        )

        self.addAction(
            qta.icon("fa.save"),
            "&Save Project",
            self.file_save,
            Qt.CTRL + Qt.Key_S
        )

        self.addAction(
            qta.icon("fa.save"),
            "Save Project &As …",
            self.file_save_as,
            Qt.CTRL + Qt.SHIFT + Qt.Key_S
        )

        self.addSeparator()

        self.addAction(
            qta.icon("fa.picture-o"),
            "Export &Image …",
            self.file_export_image,
            Qt.CTRL + Qt.Key_I
        )

        self.addAction(
            qta.icon("fa.folder"),
            "Export &Container …",
            self.file_export_container,
            Qt.CTRL + Qt.Key_C
        )

        self.addSeparator()

        self.addAction(
            qta.icon("fa.window-close"),
            "&Quit",
            self.gui.close,
            Qt.CTRL + Qt.Key_Q
        )

    def update(self):
        """
        Updates the menu.
        """
        Debug(self, ".update()", refresh=True)

    # ------------------------------------------------------------------------------------------------------------------

    def file_new(self) -> None:
        """
        Opens a project from an INI file.
        """
        Debug(self.gui, ".file_new()")

        # Stop any running calculation
        if self.gui.calculation_thread is not None:
            if self.gui.calculation_thread.isRunning():
                # Cancel the running calculation
                self.gui.interrupt_calculation()

        action = QSaveAction(
            self.gui,
            title="New Project",
            date=True,
            filename="MagnetiCalc_Project",
            extension=".ini",
            _filter="MagnetiCalc Project (*.ini)"
        )
        if action.filename:
            # This just works because the default configuration is written to the specified filename if it doesn't exist
            self.gui.switch_project(action.filename)

    def file_open(self) -> None:
        """
        Opens a project from an INI file.
        """
        Debug(self.gui, ".file_open()")

        # Stop any running calculation
        if self.gui.calculation_thread is not None:
            if self.gui.calculation_thread.isRunning():
                # Cancel the running calculation
                self.gui.interrupt_calculation()

        filename, _chosen_extension = QFileDialog.getOpenFileName(
            parent=self.gui,
            caption="Open Project",
            filter="MagnetiCalc Project (*.ini)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":
            self.gui.switch_project(filename)

    def file_save(self) -> None:
        """
        Saves the project to the currently set INI file.
        """
        Debug(self.gui, ".file_save()")

        self.gui.config.save()

    def file_save_as(self) -> None:
        """
        Saves the project to an INI file.
        """
        Debug(self.gui, ".file_save_as()")

        action = QSaveAction(
            self.gui,
            title="Save Project",
            date=True,
            filename="MagnetiCalc_Project",
            extension=".ini",
            _filter="MagnetiCalc Project (*.ini)"
        )
        if action.filename:
            self.gui.config.set_filename(action.filename)
            self.gui.config.save()

    def file_export_image(self) -> None:
        """
        Exports the currently displayed scene to a PNG file.
        """
        Debug(self.gui, ".file_export_image()")

        action = QSaveAction(
            self.gui,
            title="Save Image",
            date=True,
            filename="MagnetiCalc_Screenshot",
            extension=".png",
            _filter="PNG (*.png)"
        )
        if action.filename:
            self.gui.vispy_canvas.save_image(action.filename)

    def file_export_container(self) -> None:
        """
        Exports an HDF5 container.
        """
        Debug(self.gui, ".file_export_container()")

        ExportContainer_Dialog(self.gui).show()
