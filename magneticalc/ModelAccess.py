""" Model access module. """

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

from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Debug import Debug


class ModelAccess:
    """ Model access class. """

    # Used to detect nested accesses (which would be very bad!)
    locked = False

    # Used by L{Debug}
    DebugColor = (128, 128, 0)

    def __init__(self, gui, recalculate: bool):
        """
        Initializes model access.

        @param gui: GUI
        @param recalculate: Enable to recalculate upon exiting the context
        """
        self.gui = gui
        self.recalculate = recalculate

    def __enter__(self):
        """
        Entering the context kills possibly running calculation if recalculation is enabled.
        """
        Debug(self, ".enter()")

        Assert_Dialog(not self.locked, "Invalid model access")

        self.locked = True

        if self.recalculate:
            if self.gui.calculation_thread is not None:
                self.gui.interrupt_calculation()

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """
        Leaving the context starts recalculation if enabled; otherwise, just redraw.
        """
        Debug(self, ".exit()")

        Assert_Dialog(self.locked, "Invalid model access")

        if self.recalculate:
            if self.gui.config.get_bool("auto_calculation"):
                self.gui.recalculate()
            else:
                self.gui.redraw()

        self.locked = False
