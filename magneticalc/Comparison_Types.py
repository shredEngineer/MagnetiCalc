""" Comparison_Types module. """

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


COMPARISON_TYPE_IN_RANGE = 0


Comparison_Types_Str_Map = {
    COMPARISON_TYPE_IN_RANGE    : "In Range"
}


Comparison_Type_Fallback = COMPARISON_TYPE_IN_RANGE


def comparison_type_to_str(comparison_type: int) -> str:
    """
    Converts a comparison type to a comparison string.

    @param comparison_type: Comparison type
    @return: Comparison string
    """
    if comparison_type in Comparison_Types_Str_Map:
        return Comparison_Types_Str_Map.get(comparison_type, "")
    else:
        Assert_Dialog(
            False, f"Invalid comparison type: Defaulting to \"{Comparison_Types_Str_Map[Comparison_Type_Fallback]}\""
        )
        return Comparison_Types_Str_Map[Comparison_Type_Fallback]


def comparison_type_from_str(comparison_str: str) -> int:
    """
    Converts a comparison string to a comparison type.

    @param comparison_str: Comparison string
    @return Comparison type, or None if comparison string is invalid
    """
    result = [
        _comparison_type for _comparison_type, _comparison_str in Comparison_Types_Str_Map.items()
        if _comparison_str == comparison_str
    ]
    if len(result) == 1:
        return result[0]
    else:
        Assert_Dialog(
            False, f"Invalid comparison string: Defaulting to \"{Comparison_Types_Str_Map[Comparison_Type_Fallback]}\""
        )
        return Comparison_Type_Fallback
