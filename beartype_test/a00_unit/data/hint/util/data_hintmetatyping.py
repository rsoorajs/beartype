#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint metadata class factories** (i.e., functions automating
instantiation of objects encapsulating sample type hints).
'''

# ....................{ IMPORTS                           }....................
from beartype._util.mod.utilmodimport import (
    import_module_typing_attr_or_none,
    import_module_typingextensions_attr_or_none,
)
from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
    PepHintMetadata)
from typing import Any, Callable, Dict, Tuple

# ....................{ CONSTANTS                         }....................
_TYPING_ATTR_IMPORTERS = (
    import_module_typing_attr_or_none,
    import_module_typingextensions_attr_or_none,
)
'''
Tuple of all functions importing typing attributes from a given typing module.
'''

# ....................{ FACTORIES                         }....................
def make_hints_metadata_typing(
    # Mandatory parameters.
    typing_attr_basename: str,
    hint_metadata: Dict[str, Any],

    # Optional parameters.
    hint_maker: Callable[[Any,], Any] = lambda hint: hint,
) -> Tuple[PepHintMetadata]:
    '''
    Create and return a tuple of zero or more **typing type hint metadata
    objects** (i.e., :class:`PepHintMetadata` instances describing type hints
    originating from typing modules available under the active Python
    interpreter), depending on which typing modules are importable and which
    attributes importable from those typing modules.

    Specifically, this function returns a tuple containing:

    * If the :mod:`typing` module declares an attribute with the passed name,
      a new :class:`PepHintMetadata` instance created by passing the
      :meth:`PepHintMetadata.__init__` method:

      * A ``hint`` parameter whose value is that returned by calling the passed
        ``hint_maker`` callable passed that attribute imported from that
        module.
      * All remaining parameters from the passed ``hint_metadata`` dictionary
        as keyword arguments.

    * If the third-party :mod:`typing_extensions` module is both importable
      *and* declares an attribute with the passed name,
      a new :class:`PepHintMetadata` instance created by passing the
      :meth:`PepHintMetadata.__init__` method similar parameters.

    Attributes
    ----------
    typing_attr_basename : str
        Unqualified name of the attribute to be imported from a typing module.
    hint_metadata: Dict[str, Any]
        Dictionary of additional keyword arguments to be passed to the
        :meth:`PepHintMetadata.__init__` method for each
        :class:`PepHintMetadata` instance created by this function.
    hint_maker : Callable[[Any,], Any]
        **PEP-compliant type hint factory** (i.e., callable accepting this
        attribute imported from a typing module and returning a PEP-compliant
        type hint subscripting this attribute). Defaults to the **identity
        function** (i.e., trivially returning the passed attribute), suitable
        for unsubscripted type hints that are trivial typing attributes.

    Returns
    ----------
    Tuple[PepHintMetadata]
        Tuple of zero or more typing type hint metadata objects.
    '''
    assert isinstance(typing_attr_basename, str), (
        f'{typing_attr_basename} not string.')
    assert isinstance(hint_metadata, dict), f'{hint_metadata} not dictionary.'

    # Defer heavyweight imports.
    from beartype._util.func.utilfuncarg import (
        die_unless_func_args_len_flexible_equal)

    # If this hint factory does *NOT* accept exactly one argument, raise an
    # exception.
    die_unless_func_args_len_flexible_equal(
        func=hint_maker, func_args_len_flexible=1)
    # Else, this hint factory accepts exactly one argument.

    # List of all "PepHintMetadata" instances to be returned as a tuple.
    hints_metadata_typing = []

    # For each function importing typing attributes from a given module...
    for typing_attr_importer in _TYPING_ATTR_IMPORTERS:
        # Attribute with this name imported from that module if that module
        # declares this attribute *OR* "None" otherwise.
        typing_attr = typing_attr_importer(typing_attr_basename)

        # If that module declares this attribute...
        if typing_attr is not None:
            # Type hint synthesized from this attribute by this hint factory.
            hint = hint_maker(typing_attr)

            # Append a new "PepHintMetadata" instance encapsulating this hint.
            hint_metadata_typing = PepHintMetadata(hint=hint, **hint_metadata)

            # Append this instance to this list.
            hints_metadata_typing.append(hint_metadata_typing)

    # Return this list coerced into a tuple for caller convenience.
    return tuple(hints_metadata_typing)