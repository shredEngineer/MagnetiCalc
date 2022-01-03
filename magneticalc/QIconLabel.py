""" QIconLabel module. """

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
import qtawesome as qta
from PyQt5.Qt import QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QHBoxLayout, QLabel
from magneticalc.QLabel2 import QLabel2
from magneticalc.Theme import Theme


class QIconLabel(QHBoxLayout):
    """ QIconLabel class. """

    # Default spacing
    HorizontalSpacing = 1

    def __init__(
            self,
            text: str,
            icon: str,
            text_color: str = Theme.DarkColor,
            icon_color: str = Theme.DarkColor,
            icon_size: QSize = QSize(16, 16),
            final_stretch: bool = True,
            font: Optional[QFont] = None
    ) -> None:
        """
        Initializes the icon label.

        @param text: Label text
        @param icon: QtAwesome icon id
        @param text_color: Text color
        @param icon_color: Icon color
        @param icon_size: Icon size
        @param final_stretch: Enable to add a final stretch
        @param font: QFont
        """
        QHBoxLayout.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)

        if icon is not None:
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(icon, color=icon_color).pixmap(icon_size))
            self.addWidget(icon_label, alignment=Qt.AlignVCenter)
            self.addSpacing(self.HorizontalSpacing)

        self.addWidget(QLabel2(text, font=font, bold=True, color=text_color))

        if final_stretch:
            self.addStretch()
