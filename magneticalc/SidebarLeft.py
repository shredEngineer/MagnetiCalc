""" SidebarLeft module. """

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QSizePolicy
from magneticalc.SamplingVolume_Widget import SamplingVolume_Widget
from magneticalc.Wire_Widget import Wire_Widget


class SidebarLeft(QScrollArea):
    """ SidebarLeft class. """

    # Display settings
    MaximumWidth = 370
    VerticalSpacing = 12

    def __init__(self, gui):
        """
        Populates the left sidebar.

        @param gui: GUI
        """
        QScrollArea.__init__(self)

        self.gui = gui

        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setMaximumWidth(self.MaximumWidth)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.wire_widget = Wire_Widget(self.gui)
        layout.addWidget(self.wire_widget)

        layout.addSpacing(self.VerticalSpacing)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.sampling_volume_widget = SamplingVolume_Widget(self.gui)
        layout.addWidget(self.sampling_volume_widget)
