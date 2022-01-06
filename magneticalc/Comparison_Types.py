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


""" Comparison type: In Range. """
COMPARISON_TYPE_IN_RANGE = 0


""" Map of comparison types to names. """
Comparison_Types_Names_Map = {
    COMPARISON_TYPE_IN_RANGE    : "In Range"
}

""" Default comparison type. """
Comparison_Type_Default = COMPARISON_TYPE_IN_RANGE


def comparison_type_safe(comparison_type: int) -> int:
    """
    A valid comparison type is passed through, but an invalid comparison type converts to the default type.

    @param comparison_type: Comparison type
    @return: Safe comparison type
    """
    if comparison_type in Comparison_Types_Names_Map:
        return comparison_type
    else:
        Assert_Dialog(False, "Invalid comparison type, using fallback type")
        return Comparison_Type_Default


def comparison_type_to_name(comparison_type: int) -> str:
    """
    Converts a comparison type to a comparison name.

    @param comparison_type: Comparison type
    @return: Comparison name
    """
    return Comparison_Types_Names_Map[comparison_type_safe(comparison_type)]


def comparison_name_to_type(comparison_name: str) -> int:
    """
    Converts a comparison name to a comparison type.

    @param comparison_name: Comparison name
    @return Comparison type
    """
    return {_name: _type for _type, _name in Comparison_Types_Names_Map.items()}[comparison_name]
