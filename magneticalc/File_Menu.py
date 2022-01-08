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
from magneticalc.QtWidgets2.QSaveAction import QSaveAction
from magneticalc.Debug import Debug
from magneticalc.ExportContainer_Dialog import ExportContainer_Dialog


class File_Menu(QMenu):
    """ File_Menu class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ):
        """
        Initializes the menu.
        """
        QMenu.__init__(self, "&File")
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.addAction(
            qta.icon("fa.file"),
            "&New Project …",
            self.new_project,
            Qt.CTRL + Qt.Key_N
        )

        self.addAction(
            qta.icon("fa.folder"),
            "&Open Project …",
            self.open_project,
            Qt.CTRL + Qt.Key_O
        )

        self.addAction(
            qta.icon("fa.save"),
            "&Save Project",
            lambda: self.save_project_as() if self.gui.project.filename is None else self.gui.project.save_file(),
            Qt.CTRL + Qt.Key_S
        )

        self.addAction(
            qta.icon("fa.save"),
            "Save Project &As …",
            self.save_project_as,
            Qt.CTRL + Qt.SHIFT + Qt.Key_S
        )

        self.addAction(
            qta.icon("fa.times"),
            "Close Project",
            self.close_project,
            Qt.CTRL + Qt.Key_C
        )

        self.addSeparator()

        self.addAction(
            qta.icon("fa.picture-o"),
            "Export &Image …",
            self.export_image,
            Qt.CTRL + Qt.Key_I
        )

        self.addAction(
            qta.icon("fa.folder"),
            "&Export Container …",
            lambda: ExportContainer_Dialog(self.gui).show(),
            Qt.CTRL + Qt.Key_E
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

    def new_project(self) -> None:
        """
        Creates a new project with an INI file.
        """
        Debug(self.gui, ".new_project()")

        if self.gui.calculation_thread is not None:
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
            self.gui.project.switch(action.filename)
            self.gui.project.save_file()

    def open_project(self) -> None:
        """
        Opens a project from an INI file.
        """
        Debug(self.gui, ".open_project()")

        if self.gui.calculation_thread is not None:
            self.gui.interrupt_calculation()

        filename, _chosen_extension = QFileDialog.getOpenFileName(
            parent=self.gui,
            caption="Open Project",
            filter="MagnetiCalc Project (*.ini)",
            options=QFileDialog.DontUseNativeDialog
        )

        if filename != "":
            self.gui.project.switch(filename)

    def save_project_as(self) -> None:
        """
        Saves the project to an INI file.
        """
        Debug(self.gui, ".save_project_as()")

        action = QSaveAction(
            self.gui,
            title="Save Project",
            date=True,
            filename="MagnetiCalc_Project",
            extension=".ini",
            _filter="MagnetiCalc Project (*.ini)"
        )
        if action.filename:
            self.gui.project.save_file(filename=action.filename)

    def close_project(self) -> None:
        """
        Closes the project and loads the default project.
        """
        Debug(self.gui, ".close_project()")

        self.gui.project.close()
        self.gui.project.open_default()

    def export_image(self) -> None:
        """
        Exports the currently displayed scene to a PNG file.
        """
        Debug(self.gui, ".export_image()")

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
