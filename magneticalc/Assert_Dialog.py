""" Assert_Dialog module. """

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

import sys
from urllib.parse import urlencode, quote_plus
from magneticalc.QDialog2 import QDialog2
from magneticalc.QTextBrowser2 import QTextBrowser2
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme
from magneticalc.Version import Version, __URL__


class Assert_Dialog:
    """ Assert_Dialog class. """

    def __init__(self, assertion: bool, message: str) -> None:
        """
        Shows a user dialog if an assertion failed. Intended for beta-testing.
        This allows the user to either quit or resume (possibly resulting in unstable behaviour).
        Furthermore, it provides a link for filing an issue on GitHub (partially pre-filled).

        @param assertion: Boolean
        @param message: Error message
        """
        if assertion:
            return

        Debug(self, f": ERROR: Assertion failed: {message}", error=True)

        self._dialog = QDialog2(title="Assertion failed", width=600)

        # Generate Github issue URL
        issue_url = \
            f"{__URL__}/issues/new?" + \
            urlencode(
                {
                    "title": f"Assertion failed: {message}",
                    "labels": "bug",
                    "body":
                        f"**I discovered a bug in {Version.String}:**\n"
                        "```\n"
                        f"{message}\n"
                        "```\n\n"
                        f"**Steps to reproduce the problem:**\n\n"
                        "[_Please make sure to fill this in!_]"
                },
                quote_via=quote_plus
            )

        # HTML content
        html = f"""
            <span style="color: {Theme.MainColor};"><b>Sorry for the inconvenience!</b></span><br>
            <br>
            You seem to have discovered a bug in MagnetiCalc.<br>
            If this error persists, please
            <a href="{issue_url}">file an issue on GitHub</a>!<br>
            <br>
            <b>Error message:</b><br>
            <pre>{message}</pre>
            """

        text_browser = QTextBrowser2(html=html)
        self._dialog.addWidget(text_browser)

        self._dialog.addButtons({
            "Abort application"         : ("fa.times-circle", self._dialog.reject),
            "Resume (possibly unstable)": ("fa.play-circle", self._dialog.accept)
        })

        self._dialog.show()

        if not self._dialog.success:
            sys.exit()
