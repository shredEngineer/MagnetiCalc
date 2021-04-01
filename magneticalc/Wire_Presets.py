""" Wire_Presets module. """

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

import numpy as np


class Wire_Presets:
    """ Wire_Presets class. """

    # Preset: A straight line.
    StraightLine = {
        "id": "Straight Line",
        "points": [
            [-1/2, 0, 0],
            [+1/2, 0, 0]
        ]
    }

    # Preset: A single square loop with offset connections.
    SingleSquareLoop_Offset = {
        "id": "Single Square Loop (offset)",
        "points": [
            [-1/2, +1/2, +1/2],
            [+0/2, +1/2, +1/2],
            [+0/2, -1/2, +1/2],
            [+0/2, -1/2, -1/2],
            [+0/2, +1/2, -1/2],
            [+0/2, +1/2, +1/2],
            [+1/2, +1/2, +1/2]
        ]
    }

    # Preset: A single square loop with centered connections.
    SingleSquareLoop_Centered = {
        "id": "Single Square Loop (centered)",
        "points": [
            [-1/2, +1/2, +0/2],
            [+0/2, +1/2, +0/2],
            [+0/2, +1/2, +1/2],
            [+0/2, -1/2, +1/2],
            [+0/2, -1/2, -1/2],
            [+0/2, +1/2, -1/2],
            [+0/2, +1/2, +0/2],
            [+1/2, +1/2, +0/2]
        ]
    }

    # Preset: A "compensated" double square loop with offset connections.
    CompensatedDoubleSquareLoop_Offset = {
        "id": "Compensated Double Square Loop (offset)",
        "points": [
            [-3/6, +1/2, +1/2],
            [-1/6, +1/2, +1/2],
            [-1/6, -1/2, +1/2],
            [-1/6, -1/2, -1/2],
            [-1/6, +1/2, -1/2],
            [-1/6, +1/2, +1/2],
            [+1/6, +1/2, +1/2],
            [+1/6, +1/2, -1/2],
            [+1/6, -1/2, -1/2],
            [+1/6, -1/2, +1/2],
            [+1/6, +1/2, +1/2],
            [+3/6, +1/2, +1/2]
        ]
    }

    # Preset: A "compensated" double square loop with centered connections.
    CompensatedDoubleSquareLoop_Centered = {
        "id": "Compensated Double Square Loop (centered)",
        "points": [
            [-3/6, +1/2, +0/2],
            [-1/6, +1/2, +0/2],
            [-1/6, +1/2, +1/2],
            [-1/6, -1/2, +1/2],
            [-1/6, -1/2, -1/2],
            [-1/6, +1/2, -1/2],
            [-1/6, +1/2, +0/2],
            [+1/6, +1/2, +0/2],
            [+1/6, +1/2, -1/2],
            [+1/6, -1/2, -1/2],
            [+1/6, -1/2, +1/2],
            [+1/6, +1/2, +1/2],
            [+1/6, +1/2, +0/2],
            [+3/6, +1/2, +0/2]
        ]
    }

    # Preset: A single circular loop with offset connections.
    SingleCircularLoop_Offset = {
        "id": "Single Circular Loop (offset)",
        "points": [
            [
                0,
                -np.cos(2 * np.pi * i / 32) / 2,
                +np.sin(2 * np.pi * i / 32) / 2
            ]
            for i in range(32)
        ]
    }

    # Preset: A solenoid of 4 circular loops.
    SolenoidCircularLoops4 = {
        "id": "Solenoid: 4 circular loops",
        "points": [
            [
                i / 129 - 1 / 2,
                -np.cos(2 * np.pi * i / 32) / 2,
                +np.sin(2 * np.pi * i / 32) / 2
            ]
            for i in range(129)
        ]
    }

    # Preset: A solenoid of 8 circular loops.
    SolenoidCircularLoops8 = {
        "id": "Solenoid: 8 circular loops",
        "points": [
            [
                i / 257 - 1 / 2,
                -np.cos(2 * np.pi * i / 32) / 2,
                +np.sin(2 * np.pi * i / 32) / 2
            ]
            for i in range(257)
        ]
    }

    # Preset: A compensated solenoid of 2x 4 circular loops.
    CompensatedSolenoidCircularLoops4 = {
        "id": "Compensated Solenoid: 2x 4 circular loops",
        "points": [
            [
                i / 256 - 1/2,
                -np.cos(+2 * np.pi * i / 32) / 2,
                +np.sin(+2 * np.pi * i / 32) / 2
            ]
            for i in range(128)
        ] +
        [
            [
                i / 256,
                -np.cos(-2 * np.pi * (i + 1) / 32) / 2,
                +np.sin(-2 * np.pi * (i + 1) / 32) / 2
            ]
            for i in range(128)
        ]
    }

    # Preset: A compensated solenoid of 2x 8 circular loops.
    CompensatedSolenoidCircularLoops8 = {
        "id": "Compensated Solenoid: 2x 8 circular loops",
        "points": [
            [
                i / 512 - 1/2,
                -np.cos(+2 * np.pi * i / 32) / 2,
                +np.sin(+2 * np.pi * i / 32) / 2
            ]
            for i in range(256)
        ] +
        [
            [
                i / 512,
                -np.cos(-2 * np.pi * (i + 1) / 32) / 2,
                +np.sin(-2 * np.pi * (i + 1) / 32) / 2
            ]
            for i in range(256)
        ]
    }

    # ------------------------------------------------------------------------------------------------------------------

    # List of all above presets
    List = [
        StraightLine,
        SingleSquareLoop_Offset,
        SingleSquareLoop_Centered,
        CompensatedDoubleSquareLoop_Offset,
        CompensatedDoubleSquareLoop_Centered,
        SingleCircularLoop_Offset,
        SolenoidCircularLoops4,
        SolenoidCircularLoops8,
        CompensatedSolenoidCircularLoops4,
        CompensatedSolenoidCircularLoops8
    ]

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_by_id(_id_: str):
        """
        Selects a preset by name.

        @param _id_: Preset ID
        @return: Preset parameters (or None if ID not found)
        """
        for preset in Wire_Presets.List:
            if _id_ == preset["id"]:
                return preset
        return None
