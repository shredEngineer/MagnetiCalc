""" IconLabel module. """

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

import qtawesome as qta
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel


class IconLabel(QWidget):
    """ IconLabel class. """

    IconSize = QSize(16, 16)
    HorizontalSpacing = 1

    def __init__(
            self,
            qta_id: str,
            text: str,
            icon_color: str = "#12344a",
            label_color: str = "#12344a",
            final_stretch: bool = True
    ):
        """
        Initializes the icon label.

        @param qta_id: QtAwesome icon id
        @param text: Label text
        @param icon_color: Icon color
        @param label_color: Label color
        @param final_stretch: Enable to add a final stretch
        """
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        if qta_id is not None:
            icon = QLabel()
            icon.setPixmap(qta.icon(qta_id, color=icon_color).pixmap(self.IconSize))
            self.layout.addWidget(icon, alignment=Qt.AlignVCenter)
            self.layout.addSpacing(self.HorizontalSpacing)

        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {label_color};
            font-weight: bold;
        """)
        self.layout.addWidget(label, alignment=Qt.AlignVCenter)

        if final_stretch:
            self.layout.addStretch()

    # noinspection PyPep8Naming
    def addWidget(self, widget):
        """
        Adds widget to the horizontal layout

        @param widget: QWidget
        """
        self.layout.addWidget(widget, alignment=Qt.AlignVCenter)

    # noinspection PyPep8Naming
    def addStretch(self):
        """
        Adds stretch to the horizontal layout
        """
        self.layout.addStretch()

    # noinspection PyPep8Naming
    def addSpacing(self, value: float):
        """
        Adds spacing to the horizontal layout

        @param value: Spacing value
        """
        self.layout.addSpacing(value)
