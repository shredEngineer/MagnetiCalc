""" QDialog2 module. """

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

from typing import Optional
from PyQt5.QtCore import QEvent, pyqtSignal
from PyQt5.QtWidgets import QDialog
from magneticalc.QLayouted import QLayouted
from magneticalc.Debug import Debug


class QDialog2(QDialog, QLayouted):
    """ QDialog2 class. """

    # Signal emitted when this dialog is shown.
    dialog_shown = pyqtSignal()

    def __init__(
            self,
            title: Optional[str] = None,
            width: Optional[int] = None
    ) -> None:
        """
        Initializes QDialog2.

        @param title: Title
        @param width: Width
        """
        QDialog.__init__(self)
        QLayouted.__init__(self)
        self.install_layout(self)

        Debug(self, f": Init: {title}")

        if title:
            self.setWindowTitle(title)

        if width:
            self.setMinimumWidth(width)

        self.success = None

    def show(self):
        """
        Shows this dialog.
        """
        Debug(self, ".show()")

        self.success = self.exec() == 1

        Debug(self, f".show(): Dialog closed: success={self.success}")

    def showEvent(self, event: QEvent) -> None:
        """
        Overrides the showEvent method.

        @param event: QEvent
        """
        Debug(self, ".showEvent(): Dialog opened")

        # noinspection PyTypeChecker
        super(QDialog, self).showEvent(event)
        # noinspection PyUnresolvedReferences
        self.dialog_shown.emit()
