""" QTextBrowser2 module. """

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
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextBrowser


class QTextBrowser2(QTextBrowser):
    """ QTextBrowser2 class. """

    def __init__(
            self,
            html: Optional[str] = None
    ) -> None:
        """
        Initializes QTextBrowser2.

        @param html: HTML
        """
        QTextBrowser.__init__(self)

        self.setOpenExternalLinks(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("""
            background: palette(window);
            border: none;
            line-height: 20px;
        """)

        if html:
            self.insertHtml(html)

        # Scroll to top
        cursor = self.textCursor()
        cursor.setPosition(0)
        self.setTextCursor(cursor)

    def fit_to_contents(self) -> None:
        """
        Fit to contents.
        """
        self.setMinimumHeight(self.document().size().height())
