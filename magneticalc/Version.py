""" Version module. """

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


class Version:
    """ Version class. """

    # Major, Minor, Revision
    VERSION_MAJ = 2
    VERSION_MIN = 0
    VERSION_REV = 0

    # Compact version string
    VERSION = f"v{VERSION_MAJ}.{VERSION_MIN}.{VERSION_REV}"

    # GitHub Project URL
    GitHub_URL = "https://github.com/shredEngineer/MagnetiCalc"

    # PyPI Simple Repository URL
    PyPI_Simple_URL = "https://pypi.org/simple/magneticalc/"

    # Full application version string
    String = "MagnetiCalc " + VERSION
    Copyright = "Copyright © 2020–2022, Paul Wilhelm, M. Sc. <mailto:anfrage@paulwilhelm.de>"
    License = "ISC License (see README.md)"
