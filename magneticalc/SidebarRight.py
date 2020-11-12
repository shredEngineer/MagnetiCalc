""" SidebarRight module. """

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
from magneticalc.Display_Widget import Display_Widget
from magneticalc.Field_Widget import Field_Widget
from magneticalc.Metric_Widget import Metric_Widget
from magneticalc.Parameters_Widget import Parameters_Widget
from magneticalc.Perspective_Widget import Perspective_Widget


class SidebarRight(QScrollArea):
    """ SidebarRight class. """

    # Display settings
    MaximumWidth = 370
    VerticalSpacing = 12

    def __init__(self, gui):
        """
        Populates the right sidebar.

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

        self.field_widget = Field_Widget(self.gui)
        layout.addWidget(self.field_widget, alignment=Qt.AlignTop)

        layout.addSpacing(self.VerticalSpacing)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.metric_widget = Metric_Widget(self.gui)
        layout.addWidget(self.metric_widget, alignment=Qt.AlignTop)

        layout.addSpacing(self.VerticalSpacing)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.parameters_widget = Parameters_Widget(self.gui)
        layout.addWidget(self.parameters_widget, alignment=Qt.AlignTop)

        layout.addSpacing(self.VerticalSpacing)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.perspective_widget = Perspective_Widget(self.gui)
        layout.addWidget(self.perspective_widget, alignment=Qt.AlignTop)

        layout.addSpacing(self.VerticalSpacing)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.display_widget = Display_Widget(self.gui)
        layout.addWidget(self.display_widget, alignment=Qt.AlignTop)

        layout.addStretch()
