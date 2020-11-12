""" Groupbox module. """

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

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from magneticalc.Theme import Theme


class Groupbox(QGroupBox):
    """ Groupbox class. """

    def __init__(self, title):
        """
        Initializes the groupbox.

        @param title: Title
        """
        QGroupBox.__init__(self)

        self.setTitle(title)
        self.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid #cccccc;
                border-radius: 3px;
                margin-top: 20px;
                color: {Theme.PrimaryColor};
                font-weight: bold;
                background-color: #e5e5e5;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                background-color: palette(window);
            }}
        """)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.palette = self.palette()
        self.palette.setColor(QPalette.Button, QColor(3, 18, 14))
        self.setPalette(self.palette)

    # noinspection PyPep8Naming
    def addWidget(self, widget):
        """
        Adds widget to groupbox.

        @param widget: QWidget
        """
        self.layout.addWidget(widget)

    # noinspection PyPep8Naming
    def addSpacing(self, spacing: float):
        """
        Adds spacing to groupbox.

        @param spacing: Spacing value
        """
        self.layout.addSpacing(spacing)

    # noinspection PyPep8Naming
    def addLayout(self, layout):
        """
        Adds layout to groupbox.

        @param layout: QLayout
        """
        self.layout.addLayout(layout)
