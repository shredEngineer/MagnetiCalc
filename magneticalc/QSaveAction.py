""" QSaveAction module. """

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

import os
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from magneticalc.QMessageBox2 import QMessageBox2


class QSaveAction:
    """ QSaveAction class. """

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            gui,
            title: str,
            date: bool,
            filename: str,
            extension: str,
            filter: str,
            warn_overwrite: bool
    ) -> None:
        """
        Initializes a save dialog.

        @param gui: GUI
        @param title: Title
        @param date: Enable datetime prefix
        @param filename: Filename
        @param extension: Extension
        @param filter: Filename filters
        @param warn_overwrite: Enable to warn about overwriting an existing file
        """
        self.filename, _chosen_extension = QFileDialog.getSaveFileName(
            parent=gui,
            caption=title,
            directory=(datetime.now().strftime("%Y-%m-%d_%H-%M-%S_") if date else "") + filename,
            filter=filter,
            options=QFileDialog.DontUseNativeDialog
        )

        if self.filename == "":
            self.filename = None
            return

        _file_name, file_extension = os.path.splitext(filename)
        if file_extension.lower() != extension:
            self.filename += extension

        if warn_overwrite:
            print(filename, os.path.exists(self.filename))
            if os.path.exists(self.filename):
                messagebox = QMessageBox2(
                    title="Overwrite Existing File",
                    text="Do you want to overwrite the file?",
                    icon=QMessageBox.Question,
                    buttons=QMessageBox.Yes | QMessageBox.No,
                    default_button=QMessageBox.No
                )
                if messagebox.choice == QMessageBox.No:
                    self.filename = None
                    return
