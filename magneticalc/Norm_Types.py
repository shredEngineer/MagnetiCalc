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


""" Norm type: X. """
NORM_TYPE_X = 0

""" Norm type: Y. """
NORM_TYPE_Y = 1

""" Norm type: Z. """
NORM_TYPE_Z = 2

""" Norm type: Radius. """
NORM_TYPE_RADIUS = 3

""" Norm type: Radius X. """
NORM_TYPE_RADIUS_X = 4

""" Norm type: Radius Y. """
NORM_TYPE_RADIUS_Y = 5

""" Norm type: Radius Z. """
NORM_TYPE_RADIUS_Z = 6

""" Norm type: Radius XY. """
NORM_TYPE_RADIUS_XY = 7

""" Norm type: Radius XZ. """
NORM_TYPE_RADIUS_XZ = 8

""" Norm type: Radius YZ. """
NORM_TYPE_RADIUS_YZ = 9

""" Norm type: Angle XY. """
NORM_TYPE_ANGLE_XY = 10

""" Norm type: Angle XZ. """
NORM_TYPE_ANGLE_XZ = 11

""" Norm type: Angle YZ. """
NORM_TYPE_ANGLE_YZ = 12

""" Norm type: Divergence. """
NORM_TYPE_DIVERGENCE = 13


""" Map of norm types to names. """
Norm_Types_Names_Map = {
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

""" Default norm type. """
Norm_Type_Default = NORM_TYPE_X


def norm_type_safe(norm_type: int) -> int:
    """
    A valid norm type is passed through, but an invalid norm type converts to the default type.

    @param norm_type: Norm type
    @return: Safe norm type
    """
    if norm_type in Norm_Types_Names_Map:
        return norm_type
    else:
        Assert_Dialog(False, "Invalid norm type, using fallback type")
        return Norm_Type_Default


def norm_type_to_name(norm_type: int) -> str:
    """
    Converts a norm type to a norm name.

    @param norm_type: Norm type
    @return: Norm name
    """
    return Norm_Types_Names_Map[norm_type_safe(norm_type)]


def norm_name_to_type(norm_name: str) -> int:
    """
    Converts a norm name to a norm type.

    @param norm_name: Norm name
    @return Norm type
    """
    return {_name: _type for _type, _name in Norm_Types_Names_Map.items()}[norm_name]
