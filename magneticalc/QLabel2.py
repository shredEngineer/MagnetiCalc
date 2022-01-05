""" QLabel2 module. """

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

from typing import Optional, Union, Tuple
import qtawesome as qta
from PyQt5.Qt import QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLabel, QSizePolicy
from magneticalc.Theme import Theme


class QLabel2(QLabel):
    """ QLabel2 class. """

    DebugLabels = False

    def __init__(
            self,
            text: str,
            icon: Optional[str] = None,
            icon_color: str = Theme.DarkColor,
            icon_size: QSize = QSize(16, 16),
            expand: bool = True,
            align_right: bool = False,
            width: Optional[int] = None,
            **kwargs,
    ) -> None:
        """
        Initializes a QLabel.

        Please see L{QLabel2.set()} for supported arguments.

        @param text: Text
        @param icon: QtAwesome icon ID (optional)
        @param icon_color: Icon color
        @param icon_size: Icon size
        @param expand: Enable to expand
        @param align_right: Enable to align right
        @param width: Width (optional)
        """
        QLabel.__init__(self)

        if icon is not None:
            self.setPixmap(qta.icon(icon, color=icon_color).pixmap(icon_size))

        if expand:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        else:
            self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        if align_right:
            self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # type: ignore
        else:
            self.setAlignment(Qt.AlignVCenter)

        if width:
            self.setFixedWidth(width)

        self.set(text, **kwargs)

    def set(
            self,
            text: str,
            font: Optional[QFont] = None,
            font_size: Optional[str] = None,
            bold: bool = False,
            italic: bool = False,
            color: Union[str, Tuple[int, int, int]] = "black",
            css: Optional[str] = None
    ) -> None:
        """
        Sets the label properties.

        @param text: Text
        @param font: QFont
        @param font_size: Native font size
        @param bold: Enable for bold text
        @param italic: Enable for italic text
        @param color: Text color
        @param css: Additional CSS (optional)
        """
        self.setText(text)

        if font:
            self.setFont(font)

        stylesheet_map = {
            f"font-size: {font_size}": font_size,
            "font-weight: bold": bold,
            "font-weight: italic": italic,
            f"color: {color}": color,
            "background-color: red": self.DebugLabels
        }

        self.setStyleSheet(
            (f"{css};" if css is not None else "") +
            ";".join([string for string, condition in stylesheet_map.items() if condition])
        )
