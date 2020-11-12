""" About_Dialog module. """

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

import webbrowser
import qtawesome as qta
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton
from magneticalc.Theme import Theme
from magneticalc.Version import Version


class About_Dialog(QDialog):
    """ About_Dialog class. """

    # Window dimensions
    Width = 550
    Height = 340

    # HTML content
    HTML = f"""
        <span style="color: {Theme.PrimaryColor};"><b>{Version.String}</b></span><br>
        <br>
        Copyright © 2020, Paul Wilhelm, M. Sc.
        &lt;<a href="mailto:anfrage@paulwilhelm.de">anfrage@paulwilhelm.de</a>&gt;<br>
        <br>
        <small>
            <b>ISC License</b><br>
            <br>
            Permission to use, copy, modify, and/or distribute this software for any
            purpose with or without fee is hereby granted, provided that the above
            copyright notice and this permission notice appear in all copies.<br>
            <br>
            THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
            WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
            MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
            ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
            WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
            ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
            OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.<br>
        </small>
        <br>
        <span style="color: {Theme.PrimaryColor};">
            If you like this software, please consider buying me a coffee!&nbsp; ;)
        </span>
        """

    # Donation URL
    DonateURL = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TN6YTPVX36YHA&source=url"

    def __init__(self):
        """
        Initializes "About" dialog.
        """

        QDialog.__init__(self)

        self.setWindowTitle("About")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        text_browser = QTextBrowser()
        text_browser.setMinimumWidth(self.Width)
        text_browser.setMinimumHeight(self.Height)
        text_browser.setStyleSheet("""
            background: palette(window);
            border: none;
            line-height: 20px;
        """)
        text_browser.setOpenExternalLinks(True)
        text_browser.insertHtml(About_Dialog.HTML)
        text_browser.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(text_browser)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        button_box = QHBoxLayout()

        ok_button = QPushButton(qta.icon("fa.check"), "OK")
        ok_button.clicked.connect(self.accept)
        button_box.addWidget(ok_button)

        donate_button = QPushButton(qta.icon("fa.paypal"), "Donate 3€")
        donate_button.clicked.connect(partial(webbrowser.open, About_Dialog.DonateURL))
        button_box.addWidget(donate_button)

        layout.addLayout(button_box)

    # ------------------------------------------------------------------------------------------------------------------

    def show(self):
        """
        Shows this dialog.
        """
        self.exec()
