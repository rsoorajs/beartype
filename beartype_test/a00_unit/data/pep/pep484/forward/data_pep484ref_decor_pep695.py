#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`-compliant **stringified forward reference type hint**
(i.e., strings whose values are the names of classes and tuples of classes, one
or more of which typically have yet to be defined) :pep:`695`-compliant
decoration data submodule.

This submodule exercises stringified forward reference support implemented in
the :func:`beartype.beartype` decorator when specifically decorating callables
defining :pep:`695`-compliant **type parameter scopes** (e.g., the ``[T]`` in
``def muh_func[T](...) -> 'T':``) annotated by stringified forward references
referring to those type parameters (e.g., the ``'T'`` in that function).

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.12.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from collections.abc import Callable

# ....................{ CALLABLES                          }....................
@beartype
def suddenly_on[T](the_oceans: 'T') -> 'Callable[[], T]':
    '''
    Arbitrary callable decorated by :func:`beartype.beartype`, parametrized by a
    :pep:`695`-compliant type parameter, accepting an arbitrary parameter
    annotated by that type parameter, and returning a closure returning a value
    annotated by that type parameter as well, and annotated *only* by
    :pep:`484`-compliant stringified forward reference type hints referring to
    that type parameter.

    Yes, this edge case actually happened. You can't make bugs like this up.

    See Also
    --------
    https://github.com/beartype/beartype/issues/533
        Resolved issue validated by this callable.
    '''

    @beartype
    def chilly_streams() -> 'T':
        '''
        Arbitrary closure decorated by :func:`beartype.beartype`, returning a
        value annotated by the type parameter implicitly defined by the parent
        callable also defining this closure.
        '''

        # Return the parameter passed to that parent callable as is.
        return the_oceans

    # Return this closure.
    return chilly_streams
