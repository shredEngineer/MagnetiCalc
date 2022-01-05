""" Validatable module. """

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

from typing import Any, Callable
from magneticalc.Assert_Dialog import Assert_Dialog
from magneticalc.Debug import Debug


class Validatable(object):
    """ Validatable class. """

    def __init__(self) -> None:
        """
        Initializes a validatable object.
        """
        Debug(self, ": Init", init=True)
        self._valid = False

    @property
    def valid(self) -> bool:
        """
        @return: True if valid, False if invalid
        """
        return self._valid

    @valid.setter
    def valid(self, valid: bool) -> None:
        """
        @param valid: True if valid, False if invalid
        """
        Debug(self, f".valid = {valid}", success=valid, warning=not valid)
        self._valid = valid


def require_valid(func: Callable) -> Callable:
    """
    Decorator that requires a validatable object to be valid before calling a function.

    @param func: Method of a validatable instance
    @return: Function
    """

    def wrapper(validatable: Validatable, *args, **kwargs) -> Any:
        """
        Wrapper that requires a validatable object to be valid.

        @param validatable: Validatable instance
        @return: Result of the function
        """
        if not validatable.valid:
            Assert_Dialog(False, "Attempting to access invalidated object")
        result = func(validatable, *args, **kwargs)
        return result

    return wrapper


def validator(func: Callable) -> Callable:
    """
    Decorator that invalidates a validatable object and then validates it based on the result of calling a function.

    @param func: Method of a validatable instance
    @return: Function
    """

    def wrapper(validatable: Validatable, *args, **kwargs) -> Any:
        """
        Wrapper that invalidates a validatable object and then validates it based on the result of calling a function.

        @param validatable: Validatable instance
        @return: Result of the function
        """
        validatable.valid = False
        result = func(validatable, *args, **kwargs)
        validatable.valid = result
        return result

    return wrapper
