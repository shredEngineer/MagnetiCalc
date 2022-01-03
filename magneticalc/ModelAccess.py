""" Model access module. """

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

from __future__ import annotations
from types import TracebackType
from typing import Optional, Type
from sty import fg
from magneticalc.Debug import Debug

# Note: Workaround for type hinting
# noinspection PyUnreachableCode
if False:
    from magneticalc.GUI import GUI


class ModelAccess:
    """ Model access class. """

    # Used by L{Debug}
    DebugColor = fg.yellow

    def __init__(self, gui: GUI, recalculate: bool) -> None:
        """
        Initializes model access.

        @param gui: GUI
        @param recalculate: Enable to recalculate upon exiting the context
        """
        self.gui = gui
        self._recalculate = recalculate

    def __enter__(self) -> None:
        """
        Entering the context kills possibly running calculation if recalculation is enabled.
        """
        Debug(self, ".enter()")

        if self._recalculate:
            if self.gui.calculation_thread is not None:
                self.gui.interrupt_calculation()

    def __exit__(
            self,
            _exc_type: Optional[Type[BaseException]],
            _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Leaving the context starts recalculation if enabled; otherwise, just redraw.
        """
        Debug(self, ".exit()")

        Debug(self, f": Valid: {'None' if str(self.gui.model) == '' else self.gui.model}")

        if self._recalculate:
            if self.gui.config.get_bool("auto_calculation"):
                self.gui.recalculate()
            else:
                self.gui.redraw()
