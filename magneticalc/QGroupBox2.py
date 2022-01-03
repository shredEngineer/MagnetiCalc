""" QGroupBox2 module. """

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

from PyQt5.QtWidgets import QGroupBox
from magneticalc.QLayouted import QLayouted
from magneticalc.Theme import Theme


class QGroupBox2(QGroupBox, QLayouted):
    """ QGroupBox2 class. """

    def __init__(self, title: str) -> None:
        """
        Initializes a groupbox.

        @param title: Title
        """
        QGroupBox.__init__(self)
        QLayouted.__init__(self)
        self.install_layout(self)

        self.setTitle(title)

        self.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid #cccccc;
                border-radius: 3px;
                margin-top: 20px;
                color: {Theme.MainColor};
                font-weight: bold;
                background-color: #e5e5e5;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                background-color: palette(window);
            }}
        """)
