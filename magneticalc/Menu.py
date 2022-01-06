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
from magneticalc.Debug import Debug
from magneticalc.File_Menu import File_Menu
from magneticalc.Help_Menu import Help_Menu
from magneticalc.Options_Menu import Options_Menu
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
        self.options_menu = Options_Menu(self.gui)
        self.help_menu = Help_Menu(self.gui)

        self.gui.menuBar().addMenu(self.file_menu)
        self.gui.menuBar().addMenu(self.wire_menu)
        self.gui.menuBar().addMenu(self.view_menu)
        self.gui.menuBar().addMenu(self.options_menu)
        self.gui.menuBar().addMenu(self.help_menu)

    def reload(self) -> None:
        """
        Reloads the menu.
        """
        Debug(self, ".reload()", refresh=True)
        self.update()

    def update(self) -> None:
        """
        Updates all menus.
        """
        Debug(self, ".update()", refresh=True)
        self.file_menu.update()
        self.wire_menu.update()
        self.view_menu.update()
        self.options_menu.update()
