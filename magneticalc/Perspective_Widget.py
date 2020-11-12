""" Perspective_Widget module. """

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

from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from magneticalc.Groupbox import Groupbox
from magneticalc.HLine import HLine
from magneticalc.Perspective_Presets import Perspective_Presets
from magneticalc.Theme import Theme


class Perspective_Widget(Groupbox):
    """ Perspective_Widget class. """

    def __init__(self, gui):
        """
        Populates the widget.

        @param gui: GUI
        """
        Groupbox.__init__(self, "Perspective")

        self.gui = gui

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        planar_perspective_layout = QVBoxLayout()

        for preset in Perspective_Presets.List:

            button = QPushButton()
            button.setText(preset["id"])
            button.setStyleSheet("background-color: lightgrey")
            button.clicked.connect(
                partial(self.set_perspective, preset)
            )

            planar_perspective_layout.addWidget(button, alignment=Qt.AlignTop)

        self.addLayout(planar_perspective_layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.addWidget(HLine())

        hint_label = QLabel("Axis Colors:")
        x_label = QLabel("X")
        y_label = QLabel("Y")
        z_label = QLabel("Z")
        hint_label.setStyleSheet(f"color: {Theme.LightColor}; font-style: italic;")
        x_label.setStyleSheet("color: #cc0000; font-weight: bold;")
        y_label.setStyleSheet("color: #00cc00; font-weight: bold;")
        z_label.setStyleSheet("color: #0000cc; font-weight: bold;")
        xyz_hint_layout = QHBoxLayout()
        xyz_hint_layout.addWidget(hint_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
        xyz_hint_layout.addWidget(x_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
        xyz_hint_layout.addWidget(y_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
        xyz_hint_layout.addWidget(z_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.addLayout(xyz_hint_layout)

    def set_perspective(self, preset):
        """
        Sets display perspective.

        @param preset: Perspective preset (parameters, see VispyCanvas module)
        """
        self.gui.config.set_float("azimuth", preset["azimuth"])
        self.gui.config.set_float("elevation", preset["elevation"])
        self.gui.vispy_canvas.view_main.camera.azimuth = preset["azimuth"]
        self.gui.vispy_canvas.view_main.camera.elevation = preset["elevation"]
        self.gui.redraw()
