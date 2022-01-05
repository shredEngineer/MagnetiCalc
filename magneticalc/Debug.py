""" Debug module. """

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

from typing import Optional
from inspect import isclass, stack
from sty import Style, fg, ef


# Enable to see JIT debug output:
# import os
# os.environ["NUMBA_PARALLEL_DIAGNOSTICS"] = "4"


class Debug:
    """ Debug class. """

    # Colors
    LightColor = fg.grey
    SuccessColor = fg.green
    WarningColor = fg.magenta
    ErrorColor = fg.red

    # Enable debug output where init=True
    EnableInit = False

    # Enable debug output where refresh=True
    EnableRefresh = False

    # Block debug output from specific classes
    BlacklistEnabled = True
    Blacklist = [
        "About_Dialog",
        "CheckForUpdates_Dialog",
        "Constraint_Editor",
        "Display_Widget",
        "ExportContainer_Dialog",
        "Field_Widget",
        "Metric_Widget",
        "ModelAccess",
        "OverridePadding_Dialog",
        "Parameters_Widget",
        "Perspective_Widget",
        "QTableWidget2",
        "SamplingVolume_Widget",
        "Usage_Dialog",
        "VisPyCanvas",
        "Wire_Widget",
    ]

    def __init__(
            self,
            obj: object,
            text: str,
            color: Optional[Style] = None,
            force: bool = False,
            success: bool = False,
            warning: bool = False,
            error: bool = False,
            init: bool = False,
            refresh: bool = False
    ) -> None:
        """
        Displays a colorful debug message and the current call hierarchy.

        @param obj: Class instance
        @param text: Debug message
        @param color: Color (may be None)
        @param force: Enable to override whitelist
        @param success: Enable to set color=SuccessColor
        @param warning: Enable to set color=WarningColor and force=True
        @param error: Enable to set color=ErrorColor and force=True
        @param init: Enable to mark as init message (filtering through EnableInit)
        @param refresh: Enable to mark as refresh message (filtering through EnableRefresh)
        """
        if init and not self.EnableInit:
            return

        if refresh and not self.EnableRefresh:
            return

        if isclass(obj):
            # Called from within class method, i.e. Debug(self, …)
            name = obj.__name__
        else:
            # Called from within instance / static method
            name = type(obj).__name__

        if warning or error:
            force = True

        if not force:
            # Skip blacklisted class names
            if self.BlacklistEnabled and name in self.Blacklist:
                return

        # A class may specify its own default color
        if color is None:
            if hasattr(obj, "DebugColor"):
                color = obj.DebugColor  # type: ignore
            else:
                color = ""

        # Format call hierarchy
        hierarchy = ""
        for f in reversed(stack()[2:]):
            func_str = str(f.function)
            if func_str in ["<module>", "_run_module_as_main", "_run_code"]:
                # Called from within the main module (don't display these elements)
                continue
            if func_str == "run":
                # Called from within another thread (it is the calculation thread)
                func_str = "\tCalculationThread"
            hierarchy += func_str + "/"

        if success:
            color = self.SuccessColor

        if warning:
            color = self.WarningColor

        if error:
            color = self.ErrorColor

        print(self.LightColor + hierarchy + fg.rs + color + ef.bold + name + ef.rs + text + fg.rs + "\n", end="")
