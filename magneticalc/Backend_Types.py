""" Backend_Types module. """

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

import os
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Backend_CUDA import Backend_CUDA


def get_jit_enabled() -> bool:
    """
    Checks if JIT is enabled (or at least not explicitly disabled).

    @return: True if JIT enabled, False otherwise
    """
    return (os.environ["NUMBA_DISABLE_JIT"] == "0") if "NUMBA_DISABLE_JIT" in os.environ else True


""" Backend type: JIT. """
BACKEND_TYPE_JIT = 0

""" Backend type: CUDA. """
BACKEND_TYPE_CUDA = 1


""" Map of backend types to their availability. """
Backend_Types_Available = {
    BACKEND_TYPE_JIT :  get_jit_enabled(),
    BACKEND_TYPE_CUDA:  get_jit_enabled() and Backend_CUDA.is_available()
}


""" Map of backend types to names. """
Backend_Types_Names_Map = {
    BACKEND_TYPE_JIT:   "JIT",
    BACKEND_TYPE_CUDA:  "JIT + CUDA"
}

""" Default backend type. """
Backend_Type_Default = BACKEND_TYPE_JIT


def backend_type_safe(backend_type: int) -> int:
    """
    A valid backend type is passed through, but an invalid backend type converts to the default type.

    @param backend_type: Backend type
    @return: Safe backend type
    """
    if backend_type in Backend_Types_Names_Map:
        return backend_type
    else:
        Assert_Dialog(False, "Invalid backend type, using default type")
        return Backend_Type_Default


def backend_type_to_name(backend_type: int) -> str:
    """
    Converts a backend type to a backend name.

    @param backend_type: Backend type
    @return: Backend name
    """
    return Backend_Types_Names_Map[backend_type_safe(backend_type)]
