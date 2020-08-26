#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint globals** (i.e., constant global variables
concerning PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Generalize the die_unless_hint_pep_supported() and
#is_hint_pep_supported() functions to perform a genuine breadth-first traversal
#over all transitive arguments of the passed hint. Currently, these functions
#only shallowly inspect the first level of arguments of this hint. For
#example, if the "typing.Iterable" type is currently unsupported, then:
#    import typing
#    >>> hint_pep_unsupported = typing.Union[
#    ...     int, typing.Dict[str, typing.Iterable[str]]]
#    # This is what currently happens.
#    >>> is_hint_pep_supported(hint_pep_unsupported)
#    True
#    # This is what should happen instead.
#    >>> is_hint_pep_supported(hint_pep_unsupported)
#    False
#
#To implement this sanely, we'll probably want to define a new higher-level
#get_hint_pep_typing_deep_attrs_argless_to_args() getter calling the lower-level
#get_hint_pep_typing_attrs_argless_to_args() getter via a breadth-first traversal.
#For disambiguity, the latter getter should be renamed to
#get_hint_pep_typing_flat_attrs_argless_to_args().

# ....................{ IMPORTS                           }....................
import collections, contextlib, typing
from beartype._util.utilpy import (
    IS_PYTHON_AT_LEAST_3_6,
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_8,
)
from collections import abc as collections_abc

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
TYPING_ATTR_TO_TYPE_ORIGIN = {
    # "typing" attributes originating from builtin types.
    typing.Dict: dict,
    typing.FrozenSet: frozenset,
    typing.List: list,
    typing.Set: set,
    typing.Tuple: tuple,
    typing.Type: type,

    # "typing" attributes originating from abstract base classes (ABCs)
    # declared by the "collections.abc" submodule.
    typing.AbstractSet: collections_abc.Set,
    typing.AsyncIterable: collections_abc.AsyncIterable,
    typing.AsyncIterator: collections_abc.AsyncIterator,
    typing.Awaitable: collections_abc.Awaitable,
    typing.ByteString: collections_abc.ByteString,
    typing.Callable: collections_abc.Callable,
    typing.Container: collections_abc.Container,
    typing.Coroutine: collections_abc.Coroutine,
    typing.Generator: collections_abc.Generator,
    typing.Hashable: collections_abc.Hashable,
    typing.ItemsView: collections_abc.ItemsView,
    typing.Iterable: collections_abc.Iterable,
    typing.Iterator: collections_abc.Iterator,
    typing.KeysView: collections_abc.KeysView,
    typing.MappingView: collections_abc.MappingView,
    typing.Mapping: collections_abc.Mapping,
    typing.MutableMapping: collections_abc.MutableMapping,
    typing.MutableSequence: collections_abc.MutableSequence,
    typing.MutableSet: collections_abc.MutableSet,
    typing.Sequence: collections_abc.Sequence,
    typing.Sized: collections_abc.Sized,
    typing.ValuesView: collections_abc.ValuesView,

    # "typing" attributes originating from concrete classes declared by the
    # "collections" submodule.
    typing.ChainMap: collections.ChainMap,
    typing.Counter: collections.Counter,
    typing.DefaultDict: collections.defaultdict,
    typing.Deque: collections.deque,

    # "Protocol"-based abstract base classes (ABCs) define __subclasscheck__()
    # to return booleans rather than raise exceptions and are thus themselves
    # isinstance()-able.
    typing.SupportsAbs: typing.SupportsAbs,
    typing.SupportsBytes: typing.SupportsBytes,
    typing.SupportsComplex: typing.SupportsComplex,
    typing.SupportsInt: typing.SupportsInt,
    typing.SupportsFloat: typing.SupportsFloat,
    typing.SupportsRound: typing.SupportsRound,
}
'''
Dictionary mapping each **argumentless typing attribute** (i.e., public
attribute of the :mod:`typing` module uniquely identifying a PEP-compliant type
hints sans arguments) originating from an **origin type** (i.e.,
:func:`isinstance`-able class suitable for shallowly type-checking *all*
parameters and return values annotated with a PEP-compliant type hint
subscripting that attribute) to that type.

Since any arbitrary object is trivially type-checkable against an
:func:`isinstance`-able class by passing that object and class to the
:func:`isinstance` builtin, *all* parameters and return values annotated by
PEP-compliant type hints subscripting argumentless typing attributes listed in
this dictionary are shallowly type-checkable from wrapper functions generated
by the :func:`beartype.beartype` decorator.

Caveats
----------
**This dictionary should always be accessed in lieu of attempting to directly
access the low-level** ``__origin__`` **dunder attribute.** Various
singleton objects defined by the :mod:`typing` module (e.g.,
:attr:`typing.Any`, :attr:`typing.NoReturn`) *never* define this attribute,
while others (e.g., :attr:`typing.Union`) only conditionally define this
attribute under certain contexts to :mod:`typing` singletons that are *not*
non-:mod:`typing` superclasses. Since this attribute is obscure, fragile, and
error-prone, general-purpose logic directly accessing this attribute raises
:class:`AttributeError` exceptions under common edge cases: e.g.,

    >>> import typing

    # This is sane.
    >>> typing.List.__origin__
    list
    >>> typing.List[int].__origin__
    list

    # This is crazy.
    >>> typing.Union.__origin__
    AttributeError: '_SpecialForm' object has no attribute '__origin__'

    # This is balls crazy.
    >>> typing.Union[int].__origin__
    AttributeError: type object 'int' has no attribute '__origin__'

    # This is balls cray-cray -- the ultimate evolution of crazy.
    >>> typing.Union[int,str,].__origin__
    typing.Union

Thus this dictionary, which "fills in the gaps" by implementing this
laughably critical oversight.
'''

# If the active Python interpreter targets at least various Python versions,
# map argumentless typing attributes first introduced in all those versions.
if IS_PYTHON_AT_LEAST_3_6:
    TYPING_ATTR_TO_TYPE_ORIGIN.update({
        typing.AsyncGenerator: collections_abc.AsyncGenerator,
        typing.Collection: collections_abc.Collection,
        typing.ContextManager: contextlib.AbstractContextManager,
        typing.Reversible: collections_abc.Reversible,
    })

    if IS_PYTHON_AT_LEAST_3_7:
        TYPING_ATTR_TO_TYPE_ORIGIN.update({
            typing.AsyncContextManager: contextlib.AbstractAsyncContextManager,
            typing.OrderedDict: collections.OrderedDict,
        })

        if IS_PYTHON_AT_LEAST_3_8:
            TYPING_ATTR_TO_TYPE_ORIGIN.update({
                typing.SupportsIndex: typing.SupportsIndex,
            })


TYPING_ATTR_TO_TYPE_ORIGIN_GET = TYPING_ATTR_TO_TYPE_ORIGIN.get
'''
:meth:`dict.get` method of the :data:`TYPING_ATTR_TO_TYPE_ORIGIN` dictionary,
globalized as a trivial optimization for efficient access elsewhere.
'''

# ....................{ CONSTANTS ~ supported             }....................
TYPING_ATTRS_SUPPORTED = frozenset(
    # Tuple of every "typing" object explicitly supported by a branch of the
    # pep_code_check_hint() function generating code unique to that object,
    # deeply type-checking the passed parameter or returned value against the
    # PEP-compliant type hint annotated by a subscription of that object.
    (
        typing.Any,
        typing.Union,
    ) +

    # Tuple of every "typing" object implicitly supported by a branch of that
    # function generating code common to all such objects, only shallowly
    # type-checking the passed parameter or returned value against the
    # PEP-compliant type hint annotated by a subscription of that object.
    tuple(TYPING_ATTR_TO_TYPE_ORIGIN.keys())
)
'''
Frozen set of all **argumentless typing attributes** (i.e., public attributes
of the :mod:`typing` module uniquely identifying PEP-compliant type hints
sans arguments) supported by the :func:`beartype.beartype` decorator.

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_pep_typing_attrs_argless_to_args` getter function.
'''
