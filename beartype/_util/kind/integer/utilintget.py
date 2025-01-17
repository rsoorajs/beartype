#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **integer getteres** (i.e., low-level callables creating and
returning various integers of general-purpose interest).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from random import getrandbits

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_integer_pseudorandom_signed_32bit() -> int:
    '''
    **Pseudorandom signed 32-bit integer** (i.e., integer in the inclusive range
    ``[-2,147,483,648, 2,147,483,647]`` efficiently generated with the standard
    C-based Mersenne twister :func:`.getrandbits`).

    This integer is sufficiently large to randomly index arbitrary sequences,
    which is exactly the approach leveraged by type-checking wrapper functions
    generated by the :func:`beartype.beartype` decorator.

    Examples
    --------
    .. code-block:: pycon

       # Randomly index an arbitrary sequence efficiently.
       >>> from beartype._util.kind.integer.utilintget import (
       ...     get_integer_pseudorandom_signed_32bit)
       >>> fun_list = ['The', 'funnest', 'list', 'you', 'saw', 'today!']
       >>> fun_list[get_integer_pseudorandom_signed_32bit() % len(fun_list)]
       'funnest'
    '''

    # Tales of One-liners.
    return getrandbits(32)
