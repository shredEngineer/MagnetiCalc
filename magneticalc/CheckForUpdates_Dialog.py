""" CheckForUpdates_Dialog module. """

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

from typing import Optional, Tuple
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
        Debug(self, ": Init", init=True)

        icon, string, success, error = self.check_for_updates()

        Debug(self, f": Check for Updates ({__VERSION__URL__}): {string}", success=success, error=error)

        color = Theme.FailureColor if error else (Theme.SuccessColor if success else Theme.DialogTextColor)
        self.addLayout(
            QIconLabel(
                text=string,
                icon=icon,
                text_color=color,
                icon_color=color,
                icon_size=QSize(48, 48)
            )
        )

        if success:
            self.addSpacing(8)
            self.addWidget(QLabel2("Please update now:", italic=True))
            self.addSpacing(8)
            cmd = QTextEdit("python3 -m pip install magneticalc --upgrade")
            cmd.setFont(QFont(Theme.DefaultFontFace, 12))
            cmd.setMaximumHeight(64)
            cmd.setReadOnly(True)
            self.addWidget(cmd)

        self.addSpacing(8)

        self.addButtons({
            "Close": ("fa.check", self.accept)
        })

    def check_for_updates(self) -> Tuple[str, str, bool, bool]:
        """
        Checks for updates.

        @return: Icon, text, success flag, error flag
        """
        contents = self.get_remote_contents(url=__VERSION__URL__, timeout=2)
        if contents is None:
            return "fa.exclamation-circle", "Network Error", False, True

        version = self.parse_version(contents)
        if version is None:
            return "fa.exclamation-circle", "Invalid Format", False, True

        if version > __VERSION__:
            return "fa.info-circle", f"Newer version available ({version})", True, False
        elif version == __VERSION__:
            return "fa.check-circle", f"Up-to-date ({version})", False, False
        else:
            return "fa.exclamation-circle", f"Ahead of current release ({version})", False, True

    @staticmethod
    def get_remote_contents(url: str, timeout: int) -> Optional[str]:
        """
        Gets the contents of a remote file.

        @param url: URL
        @param timeout: Timeout (s)
        @return: Contents if successful, None otherwise
        """

        # noinspection PyBroadException
        try:
            return urlopen(url=url, timeout=timeout).read().decode("utf-8")
        except Exception:
            return None

    @staticmethod
    def parse_version(contents: str) -> Optional[str]:
        """
        Extracts and parses the version number from the raw Version.py contents.

        @param contents: Contents
        @return: Version string if successful, None otherwise
        """

        # noinspection RegExpAnonymousGroup
        pattern = re.compile(r'__VERSION__ = "v(\d+)\.(\d+)\.(\d+)"')

        # noinspection PyBroadException
        try:
            result = pattern.search(contents)
            if result is None:
                return None

            return "v" + ".".join(result.groups())
        except Exception:
            return None
