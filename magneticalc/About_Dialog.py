""" About_Dialog module. """

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

import webbrowser
from functools import partial
from magneticalc.QDialog2 import QDialog2
from magneticalc.QTextBrowser2 import QTextBrowser2
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme
from magneticalc.Version import Version


class About_Dialog(QDialog2):
    """ About_Dialog class. """

    # Donation URL
    DonationURL = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=TN6YTPVX36YHA&source=url"

    # HTML content
    HTML = f"""
        <span style="color: {Theme.MainColor};"><b>{Version.String}</b></span><br>
        <br>
        Copyright © 2020–2021, Paul Wilhelm, M. Sc.
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
        <span style="color: {Theme.MainColor}; font-weight: bold;">
            If you like this software, please consider buying me a coffee!&nbsp; :)
        </span>
        <br>
        """

    def __init__(self) -> None:
        """
        Initializes "About" dialog.
        """
        QDialog2.__init__(self, title="About", width=640)
        Debug(self, ": Init")

        text_browser = QTextBrowser2(html=self.HTML)
        self.dialog_shown.connect(text_browser.fit_to_contents)
        self.addWidget(text_browser)

        buttons = self.addButtons({
            "OK"            : ("fa.check", self.accept),
            "Donate 3€ …"   : ("fa.paypal", partial(webbrowser.open, About_Dialog.DonationURL))
        })
        buttons[0].setFocus()
