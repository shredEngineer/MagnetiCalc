""" Norm_Types module. """

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

from magneticalc.Assert_Dialog import Assert_Dialog


NORM_TYPE_X = 0
NORM_TYPE_Y = 1
NORM_TYPE_Z = 2
NORM_TYPE_RADIUS = 3
NORM_TYPE_RADIUS_X = 4
NORM_TYPE_RADIUS_Y = 5
NORM_TYPE_RADIUS_Z = 6
NORM_TYPE_RADIUS_XY = 7
NORM_TYPE_RADIUS_XZ = 8
NORM_TYPE_RADIUS_YZ = 9
NORM_TYPE_ANGLE_XY = 10
NORM_TYPE_ANGLE_XZ = 11
NORM_TYPE_ANGLE_YZ = 12
NORM_TYPE_DIVERGENCE = 13


Norm_Types_Str_Map = {
    NORM_TYPE_X             : "X",
    NORM_TYPE_Y             : "Y",
    NORM_TYPE_Z             : "Z",
    NORM_TYPE_RADIUS        : "Radius",
    NORM_TYPE_RADIUS_X      : "Radius X",
    NORM_TYPE_RADIUS_Y      : "Radius Y",
    NORM_TYPE_RADIUS_Z      : "Radius Z",
    NORM_TYPE_RADIUS_XY     : "Radius XY",
    NORM_TYPE_RADIUS_XZ     : "Radius XZ",
    NORM_TYPE_RADIUS_YZ     : "Radius YZ",
    NORM_TYPE_ANGLE_XY      : "Angle XY",
    NORM_TYPE_ANGLE_XZ      : "Angle XZ",
    NORM_TYPE_ANGLE_YZ      : "Angle YZ",
    NORM_TYPE_DIVERGENCE    : "Divergence",
}


Norm_Types_Fallback = NORM_TYPE_X


def norm_type_to_str(norm_type: int) -> str:
    """
    Converts a norm type to a norm string.

    @param norm_type: Norm type
    @return: Norm string
    """
    if norm_type in Norm_Types_Str_Map:
        return Norm_Types_Str_Map.get(norm_type, "")
    else:
        Assert_Dialog(False, f"Invalid norm type: Defaulting to \"{Norm_Types_Str_Map[Norm_Types_Fallback]}\"")
        return Norm_Types_Str_Map[Norm_Types_Fallback]


def norm_type_from_str(norm_str: str) -> int:
    """
    Converts a norm string to a norm type.

    @param norm_str: Norm string
    @return Norm type
    """
    result = [_norm_type for _norm_type, _norm_str in Norm_Types_Str_Map.items() if _norm_str == norm_str]
    if len(result) == 1:
        return result[0]
    else:
        Assert_Dialog(False, f"Invalid norm string: Defaulting to \"{Norm_Types_Str_Map[Norm_Types_Fallback]}\"")
        return Norm_Types_Fallback
