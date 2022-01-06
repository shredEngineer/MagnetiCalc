""" View_Menu module. """

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
from PyQt5.QtWidgets import QMenu
from magneticalc.QCheckboxConfig import QCheckboxConfig
from magneticalc.Debug import Debug


class View_Menu(QMenu):
    """ View_Menu class. """

    def __init__(
            self,
            gui: GUI  # type: ignore
    ):
        QMenu.__init__(self, "&View")
        Debug(self, ": Init", init=True)
        self.gui = gui

        self.checkbox_config = QCheckboxConfig(gui=self.gui)
        self.addAction(
            self.checkbox_config.add("Show Wire Segments", "show_wire_segments", self.gui.redraw)
        )
        self.addAction(
            self.checkbox_config.add("Show Wire Points", "show_wire_points", self.gui.redraw)
        )
        self.addSeparator()
        self.addAction(
            self.checkbox_config.add("Show Colored Labels", "show_colored_labels", self.gui.redraw)
        )
        self.addAction(
            self.checkbox_config.add("Show Gauss instead of Tesla", "show_gauss", self.on_show_gauss_changed)
        )
        self.addSeparator()
        self.addAction(
            self.checkbox_config.add("Show Coordinate System", "show_coordinate_system", self.gui.redraw)
        )
        self.addAction(
            self.checkbox_config.add("Show Perspective Info", "show_perspective_info", self.gui.redraw)
        )
        self.addSeparator()
        self.addAction(
            self.checkbox_config.add("Dark Background", "dark_background", self.gui.redraw)
        )

    def update(self):
        """
        Updates the menu.
        """
        Debug(self, ".update()", refresh=True)

        self.gui.blockSignals(True)
        self.checkbox_config.reload()
        self.gui.blockSignals(False)

    # ------------------------------------------------------------------------------------------------------------------

    def on_show_gauss_changed(self) -> None:
        """
        Gets called when the "Show Gauss instead of Tesla" option changed.
        """
        self.gui.sidebar_right.metric_widget.update()
        self.gui.vispy_canvas.delete_field_labels()
        self.gui.redraw()
