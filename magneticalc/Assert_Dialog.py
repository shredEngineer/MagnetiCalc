""" Assert_Dialog module. """

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

import sys
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme
from magneticalc.Version import Version
from urllib.parse import urlencode, quote_plus


class Assert_Dialog:
    """ Assert_Dialog class. """

    # Window dimensions
    Width = 600

    def __init__(self, assertion: bool, message: str):
        """
        Shows a user dialog if an assertion failed. Intended for beta-testing.
        This allows the user to either quit or resume (possibly resulting in unstable behaviour).
        Furthermore, it provides a link for filing an issue on GitHub (partially pre-filled).

        @param assertion: Boolean
        @param message: Error message
        """
        self.assertion = assertion
        self.message = message

        if assertion:
            return

        Debug(self, f": Failed: {message}", color=Theme.WarningColor, force=True)

        self.dialog = QDialog()

        self.dialog.setWindowTitle("Assertion failed")

        layout = QVBoxLayout()
        self.dialog.setLayout(layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Generate Github issue URL
        issue_url = \
            f"https://github.com/shredEngineer/MagnetiCalc/issues/new?" + \
            urlencode(
                {
                    "title": f"Assertion failed: {self.message}",
                    "labels": "bug",
                    "body":
                        f"**I discovered a bug in {Version.String}:**\n"
                        "```\n"
                        f"{self.message}\n"
                        "```\n\n"
                        f"**Steps to reproduce the problem:**\n\n"
                        "[_Please make sure to fill this in!_]"
                },
                quote_via=quote_plus
            )

        # HTML content
        html = f"""
            <span style="color: {Theme.PrimaryColor};"><b>Sorry for the inconvenience!</b></span><br>
            <br>
            You seem to have discovered a bug in MagnetiCalc.<br>
            If this error persists, please
            <a href="{issue_url}">file an issue on GitHub</a>!<br>
            <br>
            <b>Error message:</b><br>
            <pre>{self.message}</pre>
            """

        text_browser = QTextBrowser()
        text_browser.setMinimumWidth(self.Width)
        text_browser.setStyleSheet("""
            background: palette(window);
            border: none;
            line-height: 20px;
        """)
        text_browser.setOpenExternalLinks(True)
        text_browser.insertHtml(html)
        text_browser.setFocusPolicy(Qt.NoFocus)
        cursor = text_browser.textCursor()
        cursor.setPosition(0)
        text_browser.setTextCursor(cursor)
        layout.addWidget(text_browser, alignment=Qt.AlignTop)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        button_box = QHBoxLayout()

        ok_button = QPushButton(qta.icon("fa.times-circle"), "Abort application")
        ok_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button, alignment=Qt.AlignBottom)

        donate_button = QPushButton(qta.icon("fa.play-circle"), "Resume (possibly unstable)")
        donate_button.clicked.connect(self.accept)
        button_box.addWidget(donate_button, alignment=Qt.AlignBottom)

        layout.addLayout(button_box)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.dialog.exec()

    # ------------------------------------------------------------------------------------------------------------------

    def reject(self):
        """
        User chose to abort.
        """
        self.dialog.reject()

        sys.exit()

    def accept(self):
        """
        User chose to resume.
        """
        self.dialog.accept()
