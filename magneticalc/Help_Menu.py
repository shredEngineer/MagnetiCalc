""" Help_Menu module. """

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
from PyQt5.QtWidgets import QMenu
from magneticalc.About_Dialog import About_Dialog
from magneticalc.CheckForUpdates_Dialog import CheckForUpdates_Dialog
from magneticalc.Debug import Debug
from magneticalc.Usage_Dialog import Usage_Dialog
from magneticalc.Version import __URL__


class Help_Menu(QMenu):
    """ Help_Menu class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ):
        """
        Initializes the menu.
        """
        QMenu.__init__(self, "&Help")
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.addAction(qta.icon("fa.info"), "&Usage …", lambda: Usage_Dialog().show(), Qt.Key_F1)
        self.addSeparator()
        self.addAction(
            qta.icon("fa.newspaper-o"), "&Check for Updates …", lambda: CheckForUpdates_Dialog().show()
        )
        self.addAction(
            qta.icon("fa.github"),
            "&GitHub Repository …",
            partial(webbrowser.open, __URL__)  # type: ignore
        )
        self.addSeparator()
        self.addAction(qta.icon("fa.coffee"), "&About …", lambda: About_Dialog().show())

    def update(self):
        """
        Updates the menu.
        """
        Debug(self, ".update()", refresh=True)
