""" QHLine module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm <anfrage@paulwilhelm.de>
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

from PyQt5.QtWidgets import QFrame


class QHLine(QFrame):
    """ QHLine class. """

    # Default spacing
    VerticalSpacing = 12

    def __init__(self) -> None:
        """
        Creates a horizontal line.
        """
        QFrame.__init__(self)

        self.setFixedHeight(self.VerticalSpacing)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet(f"""
            border-top: 1px solid #cccccc;
            border-bottom: 1px solid #f0f0f0;
            margin-top: {self.VerticalSpacing // 2 - 1}px;
            margin-bottom: {self.VerticalSpacing // 2 - 1}px;
        """)
