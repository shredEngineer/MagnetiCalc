""" CheckForUpdates_Dialog module. """

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

import re
from urllib.request import urlopen
from PyQt5.Qt import QFont, QSize
from PyQt5.QtWidgets import QTextEdit
from magneticalc.QDialog2 import QDialog2
from magneticalc.QIconLabel import QIconLabel
from magneticalc.QLabel2 import QLabel2
from magneticalc.Debug import Debug
from magneticalc.Theme import Theme
from magneticalc.Version import __VERSION__, __VERSION__URL__


class CheckForUpdates_Dialog(QDialog2):
    """ CheckForUpdates_Dialog class. """

    def __init__(self) -> None:
        """
        Prepares the 'Check for Updates' dialog.
        """
        QDialog2.__init__(self, title="Check for Updates", width=500)
        Debug(self, ": Init")

        update_hint = False

        # noinspection PyBroadException
        try:
            version_py = urlopen(__VERSION__URL__, timeout=2).read().decode("utf-8")
        except Exception:
            icon, string, color = "fa.exclamation-circle", f"Network Error", Theme.FailureColor
        else:
            # noinspection RegExpAnonymousGroup
            pattern = re.compile(r'__VERSION__ = "v(\d+)\.(\d+)\.(\d+)"')
            # noinspection PyBroadException
            try:
                version = "v" + ".".join(pattern.search(version_py).groups())
            except Exception:
                icon, string, color = "fa.exclamation-circle", f"Invalid Format", Theme.FailureColor
            else:
                if version > __VERSION__:
                    icon, string, color = "fa.info-circle", f"Newer version available: {version}", Theme.SuccessColor
                    update_hint = True
                elif version == __VERSION__:
                    icon, string, color = "fa.check-circle", f"Up-to-date: {version}", Theme.MainColor
                else:
                    icon, string, color = \
                        "fa.exclamation-circle", f"Ahead of current release {version}", Theme.FailureColor

        Debug(self, f": Check for Updates ({__VERSION__URL__}): {string}", color=color)
        icon_label = QIconLabel(
            text=string,
            icon=icon,
            text_color=color,
            icon_color=color,
            icon_size=QSize(32, 32),
            font=QFont(Theme.DefaultFontFace, 14)
        )
        self.addLayout(icon_label)

        if update_hint:
            self.addSpacing(8)
            self.addWidget(QLabel2("Please update now:", italic=True))
            self.addSpacing(8)
            cmd = QTextEdit("python3 -m pip install magneticalc --upgrade")
            cmd.setFont(QFont(Theme.DefaultFontFace, 12))
            cmd.setMaximumHeight(64)
            cmd.setReadOnly(True)
            self.add_element(cmd)

        self.addSpacing(8)

        self.addButtons({
            "Close": ("fa.check", self.accept)
        })
