""" Wire_Presets module. """

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

from typing import Optional, Dict
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

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    def get_phase_jumping_toroidal_loop(
            n_points: int, n_phase_jumps: int,
            toroidal_radius: float, poloidal_radius: float,
            toroidal_freq: float, poloidal_freq: float
    ) -> np.ndarray:
        """
        Generates a (phase-jumping) toroidal loop.

        @param n_points: Number of points
        @param n_phase_jumps: Number of phase jumps
        @param toroidal_radius: Toroidal radius
        @param poloidal_radius: Poloidal radius
        @param toroidal_freq: Toroidal frequency
        @param poloidal_freq: Poloidal frequency
        """
        def rotate_xy(V: np.ndarray, A: float) -> np.ndarray:
            """
            Rotates a 3D vector some angle in the XY-plane.

            @param V: 3D vector
            @param A: Angle in radians
            """
            return np.array(
                [V[0] * np.cos(A) - V[1] * np.sin(A), V[0] * np.sin(A) + V[1] * np.cos(A), V[2]]
            )

        wire_points = []
        for t in range(n_points + 1):
            phase_toroidal = 2 * np.pi * t / n_points * toroidal_freq
            phase_jump_poloidal = (1 if (t // (n_points / n_phase_jumps)) % 2 == 0 else -1)
            phase_poloidal = 2 * np.pi * t / n_points * poloidal_freq * phase_jump_poloidal + np.pi / 2
            phase_poloidal = np.fmod(phase_poloidal, 2 * np.pi)
            p_toroidal = toroidal_radius * np.array([np.cos(phase_toroidal), np.sin(phase_toroidal), 0])
            p_poloidal = poloidal_radius * np.array([0, np.cos(phase_poloidal), np.sin(phase_poloidal)])
            wire_points.append(p_toroidal + rotate_xy(p_poloidal, phase_toroidal + np.pi / 2))
        return np.array(wire_points)

    # Preset: A phase-jumping toroidal loop: 8 turns.
    # noinspection PyUnresolvedReferences
    PhaseJumpingToroidalLoop8 = {
        "id": "Phase-jumping Toroidal Loop: 8 turns",
        "points": get_phase_jumping_toroidal_loop.__func__(
            n_points=640, n_phase_jumps=8,
            toroidal_radius=1, poloidal_radius=.5,
            toroidal_freq=1, poloidal_freq=8
        )
    }
    # Preset: A phase-jumping toroidal loop: 32 turns.
    # noinspection PyUnresolvedReferences
    PhaseJumpingToroidalLoop16 = {
        "id": "Phase-jumping Toroidal Loop: 16 turns",
        "points": get_phase_jumping_toroidal_loop.__func__(
            n_points=640, n_phase_jumps=16,
            toroidal_radius=1, poloidal_radius=.5,
            toroidal_freq=1, poloidal_freq=16
        )
    }
    # Preset: A phase-jumping toroidal loop: 32 turns.
    # noinspection PyUnresolvedReferences
    PhaseJumpingToroidalLoop32 = {
        "id": "Phase-jumping Toroidal Loop: 32 turns",
        "points": get_phase_jumping_toroidal_loop.__func__(
            n_points=640, n_phase_jumps=32,
            toroidal_radius=1, poloidal_radius=.5,
            toroidal_freq=1, poloidal_freq=32
        )
    }

    # Preset: A toroidal loop: 8 turns.
    # noinspection PyUnresolvedReferences
    ToroidalLoop8 = {
        "id": "Toroidal Loop: 8 turns",
        "points": get_phase_jumping_toroidal_loop.__func__(
            n_points=640, n_phase_jumps=1,
            toroidal_radius=1, poloidal_radius=.5,
            toroidal_freq=1, poloidal_freq=8
        )
    }

    # Preset: A toroidal loop: 16 turns.
    # noinspection PyUnresolvedReferences
    ToroidalLoop16 = {
        "id": "Toroidal Loop: 16 turns",
        "points": get_phase_jumping_toroidal_loop.__func__(
            n_points=640, n_phase_jumps=1,
            toroidal_radius=1, poloidal_radius=.5,
            toroidal_freq=1, poloidal_freq=16
        )
    }

    # Preset: A toroidal loop: 32 turns.
    # noinspection PyUnresolvedReferences
    ToroidalLoop32 = {
        "id": "Toroidal Loop: 32 turns",
        "points": get_phase_jumping_toroidal_loop.__func__(
            n_points=640, n_phase_jumps=1,
            toroidal_radius=1, poloidal_radius=.5,
            toroidal_freq=1, poloidal_freq=32
        )
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
        CompensatedSolenoidCircularLoops8,
        PhaseJumpingToroidalLoop8,
        PhaseJumpingToroidalLoop16,
        PhaseJumpingToroidalLoop32,
        ToroidalLoop8,
        ToroidalLoop16,
        ToroidalLoop32,
    ]

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_by_id(_id_: str) -> Optional[Dict]:
        """
        Selects a preset by name.

        @param _id_: Preset ID
        @return: Preset parameters (or None if ID not found)
        """
        for preset in Wire_Presets.List:
            if _id_ == preset["id"]:
                return preset
        return None
