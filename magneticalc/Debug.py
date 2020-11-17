""" Debug module. """

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

from inspect import isclass, stack
from colorit import color_front, bold


# Enable to see JIT debug output
# import os
# os.environ["NUMBA_PARALLEL_DIAGNOSTICS"] = "4"


class Debug:
    """ Debug class. """

    # Enable debug output from specific classes only
    Whitelist = [
        "About_Dialog",
        "Assert_Dialog",
        "BiotSavart_CUDA",
        "BiotSavart_JIT",
        "CalculationThread",
        # "Config",
        "Constants",
        "Constraint",
        "Constraint_Editor",
        "Display_Widget",
        "Field",
        "Field_Widget",
        "Groupbox",
        "GUI",
        "HLine",
        "IconLabel",
        "Menu",
        "Metric",
        "Metric_Presets",
        "Metric_Widget",
        "Model",
        "ModelAccess",
        "Parameters",
        "Parameters_Widget",
        "Perspective_Presets",
        "Perspective_Widget",
        "SamplingVolume",
        "SamplingVolume_Widget",
        "SidebarLeft",
        "SidebarRight",
        "SliderFloat",
        "Statusbar",
        # "Table",
        "Theme",
        "Usage_Dialog",
        "Version",
        # "VispyCanvas",
        "Wire",
        "Wire_Presets",
        "Wire_Widget"
    ]

    def __init__(self, obj, text: str, color=None, force: bool = False):
        """
        Displays a colorful debug message and the current call hierarchy.

        @param obj: Class instance
        @param text: Debug message
        @param color: Color (may be None)
        @param force: Enable to override whitelist
        """
        if isclass(obj):
            # Called from within class method, i.e. Debug(self, ...)
            name = obj.__name__
        else:
            # Called from within instance / static method
            name = type(obj).__name__

        if not force:
            # Skip non-whitelisted class names
            if name not in self.Whitelist:
                return

        # A class may specify its own default color
        if color is None:
            if hasattr(obj, "DebugColor"):
                color = obj.DebugColor
            else:
                color = (0, 0, 0)

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

        if isinstance(color, str):
            # Convert hex color string ("#abcdef") to RGB tuple
            color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

        if color == (0, 0, 0):
            # Allow a terminal use its own foreground color
            color_text = bold(name) + text
        else:
            color_text = color_front(bold(name), *color) + color_front(text, *color)

        print(color_front(hierarchy, 128, 128, 128) + color_text + "\n", end="")
