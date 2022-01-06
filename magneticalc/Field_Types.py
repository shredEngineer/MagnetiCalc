""" Field_Types module. """

#  ISC License
#
#  Copyright (c) 2020–2022, Paul Wilhelm <anfrage@paulwilhelm.de>
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


""" Field type: A-Field. """
FIELD_TYPE_A = 0

""" Field type: B-Field. """
FIELD_TYPE_B = 1


""" Map of field types to names. """
Field_Types_Names_Map = {
    FIELD_TYPE_A    :   "A-Field (Vector Potential)",
    FIELD_TYPE_B    :   "B-Field (Flux Density)"
}

""" Default field type. """
Field_Type_Default = FIELD_TYPE_A


def field_type_safe(field_type: int) -> int:
    """
    A valid field type is passed through, but an invalid field type converts to the default type.

    @param field_type: Field type
    @return: Safe field type
    """
    if field_type in Field_Types_Names_Map:
        return field_type
    else:
        Assert_Dialog(False, "Invalid field type, using fallback type")
        return Field_Type_Default
