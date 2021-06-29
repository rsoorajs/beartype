#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **bare PEP-compliant type hint representations** (i.e., global
constants pertaining to machine-readable strings returned by the :func:`repr`
builtin suffixed by *no* "["- and "]"-delimited subscription representations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.data.hint.pep.sign import datapepsigns
from beartype._util.data.hint.pep.sign.datapepsigncls import HintSign
from beartype._util.data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    # HintSignAnnotated,
    # HintSignAny,
    HintSignAsyncContextManager,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAsyncGenerator,
    HintSignAwaitable,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    # HintSignClassVar,
    HintSignCollection,
    # HintSignConcatenate,
    HintSignContainer,
    HintSignCoroutine,
    HintSignContextManager,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    # HintSignFinal,
    HintSignForwardRef,
    HintSignFrozenSet,
    HintSignGenerator,
    # HintSignGeneric,
    # HintSignHashable,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    # HintSignLiteral,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    # HintSignNamedTuple,
    # HintSignNewType,
    # HintSignOptional,
    HintSignOrderedDict,
    # HintSignParamSpec,
    # HintSignParamSpecArgs,
    # HintSignProtocol,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    # HintSignSized,
    HintSignPattern,
    HintSignTuple,
    HintSignType,
    HintSignTypeVar,
    # HintSignTypedDict,
    # HintSignUnion,
    HintSignValuesView,
)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_9,
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_3_6,
)
from typing import Dict, FrozenSet, Set

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MAPPINGS ~ repr                   }....................
# The majority of this dictionary is initialized with automated inspection
# below in the _init() function. The *ONLY* key-value pairs explicitly defined
# here are those *NOT* amenable to such inspection.
HINT_BARE_REPR_TO_SIGN: Dict[str, HintSign] = {
    # ..................{ PEP 484                           }..................
    #FIXME: This is a bit odd. If an unsubscripted "typing.Protocol" is
    #ignorable, why wouldn't an unsubscripted "typing.Generic" be ignorable as
    #well? Consider excising this, please.

    # Identify the unsubscripted PEP 484-compliant "Generic" ABC (explicitly
    # equivalent under PEP 484 to the "Generic[Any]" subscription and thus
    # possibly conveying meaningful semantics) by this sign.
    # Under ...
    #
    # Note this *ONLY* applies to Python >= 3.7. Under Python 3.6,
    # "repr(typing.Generic) == 'typing.Generic'", which is thus already handled
    # by automated inspection below.
    # "<class 'typing.Generic'>":            HintSignGeneric,
    # "<class 'typing_extensions.Generic'>": HintSignGeneric,

    # ..................{ PEP 585                           }..................
    # For synchronicity, these key-value pairs are intentionally defined in the
    # same order as the official list in PEP 585 itself.
    'tuple': HintSignTuple,
    'list': HintSignList,
    'dict': HintSignDict,
    'set': HintSignSet,
    'frozenset': HintSignFrozenSet,
    'type': HintSignType,
    'collections.deque': HintSignDeque,
    'collections.defaultdict': HintSignDefaultDict,
    'collections.OrderedDict': HintSignOrderedDict,
    'collections.Counter': HintSignCounter,
    'collections.ChainMap': HintSignChainMap,
    'collections.abc.Awaitable': HintSignAwaitable,
    'collections.abc.Coroutine': HintSignCoroutine,
    'collections.abc.AsyncIterable': HintSignAsyncIterable,
    'collections.abc.AsyncIterator': HintSignAsyncIterator,
    'collections.abc.AsyncGenerator': HintSignAsyncGenerator,
    'collections.abc.Iterable': HintSignIterable,
    'collections.abc.Iterator': HintSignIterator,
    'collections.abc.Generator': HintSignGenerator,
    'collections.abc.Reversible': HintSignReversible,
    'collections.abc.Container': HintSignContainer,
    'collections.abc.Collection': HintSignCollection,
    'collections.abc.Callable': HintSignCallable,
    'collections.abc.Set': HintSignAbstractSet,
    'collections.abc.MutableSet': HintSignMutableSet,
    'collections.abc.Mapping': HintSignMapping,
    'collections.abc.MutableMapping': HintSignMutableMapping,
    'collections.abc.Sequence': HintSignSequence,
    'collections.abc.MutableSequence': HintSignMutableSequence,
    'collections.abc.ByteString': HintSignByteString,
    'collections.abc.MappingView': HintSignMappingView,
    'collections.abc.KeysView': HintSignKeysView,
    'collections.abc.ItemsView': HintSignItemsView,
    'collections.abc.ValuesView': HintSignValuesView,
    'contextlib.AbstractContextManager': HintSignContextManager,
    'contextlib.AbstractAsyncContextManager': HintSignAsyncContextManager,
    're.Pattern': HintSignPattern,
    're.Match': HintSignMatch,
}
'''
Dictionary mapping from the **bare PEP-compliant type hint representations**
(i.e., machine-readable strings returned by the :func:`repr` builtin suffixed
by *no* "["- and "]"-delimited subscription representations) of all hints
uniquely identifiable by those representations to their identifying signs.
'''

# ....................{ MAPPINGS ~ type                   }....................
# Initialized with automated inspection below in the _init() function.
HINT_TYPE_NAME_TO_SIGN: Dict[str, HintSign] = {}
'''
Dictionary mapping from the fully-qualified classnames of all PEP-compliant
type hints uniquely identifiable by those classnames to their identifying
signs.
'''

# ....................{ SETS ~ deprecated                 }....................
# Initialized with automated inspection below in the _init() function.
HINT_BARE_REPRS_DEPRECATED: FrozenSet[str] = None  # type: ignore[assignment]
'''
Frozen set of all **bare deprecated PEP-compliant type hint representations**
(i.e., machine-readable strings returned by the :func:`repr` builtin suffixed
by *no* "["- and "]"-delimited subscription representations for all obsoleted
hints, often by equivalent hints standardized under more recent PEPs).
'''


# Initialized with automated inspection below in the _init() function.
HINT_PEP484_BARE_REPRS_DEPRECATED: FrozenSet[str] = None  # type: ignore[assignment]
'''
Frozen set of all **bare deprecated** :pep:`484`-compliant **type hint
representations** (i.e., machine-readable strings returned by the :func:`repr`
builtin suffixed by *no* "["- and "]"-delimited subscription representations
for all :pep:`484`-compliant type hints obsoleted by :pep:`585`-compliant
subscriptable classes).
'''

# ....................{ SETS ~ ignorable                  }....................
# The majority of this dictionary is initialized with automated inspection
# below in the _init() function. The *ONLY* key-value pairs explicitly defined
# here are those *NOT* amenable to such inspection.
HINT_REPRS_IGNORABLE = {
    # ..................{ NON-PEP                           }..................
    # The PEP-noncompliant builtin "object" type is the transitive superclass
    # of all classes, parameters and return values annotated as "object"
    # unconditionally match *ALL* objects under isinstance()-based type
    # covariance and thus semantically reduce to unannotated parameters and
    # return values. This is literally the "beartype.cave.AnyType" type.
    "<class 'object'>",

    # ..................{ PEP 484                           }..................
    # The "Generic" superclass imposes no constraints and is thus also
    # semantically synonymous with the ignorable PEP-noncompliant
    # "beartype.cave.AnyType" and hence "object" types. Since PEP
    # 484 stipulates that *ANY* unsubscripted subscriptable PEP-compliant
    # singleton including "typing.Generic" semantically expands to that
    # singelton subscripted by an implicit "Any" argument, "Generic"
    # semantically expands to the implicit "Generic[Any]" singleton.
    "<class 'typing.Generic'>",
    "<class 'typing_extensions.Generic'>",

    # ..................{ PEP 544                           }..................
    # Note that ignoring the "typing.Protocol" superclass is vital here. For
    # unknown and presumably uninteresting reasons, *ALL* possible objects
    # satisfy this superclass. Ergo, this superclass is synonymous with the
    # "object" root superclass: e.g.,
    #     >>> import typing as t
    #     >>> isinstance(object(), t.Protocol)
    #     True
    #     >>> isinstance('wtfbro', t.Protocol)
    #     True
    #     >>> isinstance(0x696969, t.Protocol)
    #     True
    "<class 'typing.Protocol'>",
    "<class 'typing_extensions.Protocol'>",
}
'''
Frozen set of all **shallowly ignorable PEP-compliant type hint
representations** (i.e., machine-readable strings returned by the :func:`repr`
builtin for all PEP-compliant type hints that are unconditionally ignorable by
the :func:`beartype.beartype` decorator in *all* possible contexts)

Caveats
----------
**The high-level**
:func:`beartype._util.hint.pep.utilhinttest.is_hint_ignorable` **tester
function should always be called in lieu of testing type hints against this
low-level set.** This set is merely shallow and thus excludes **deeply
ignorable type hints** (e.g., :data:`Union[Any, bool, str]`). Since there exist
a countably infinite number of deeply ignorable type hints, this set is
necessarily constrained to the substantially smaller finite subset of only
shallowly ignorable type hints.
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ..................{ EXTERNALS                         }..................
    # Defer initialization-specific imports.
    from beartype._util.data.hint.pep.datapepmodule import (
        HINT_PEP_MODULE_NAMES)

    # Permit redefinition of these globals below.
    global \
        HINT_BARE_REPRS_DEPRECATED, \
        HINT_REPRS_IGNORABLE

    # ..................{ HINTS                             }..................
    # Length of the ignorable substring prefixing the name of each sign.
    _HINT_SIGN_PREFIX_LEN = len('HintSign')

    # ..................{ HINTS ~ deprecated                }..................
    # Set of the unqualified names of all deprecated PEP 484-compliant typing
    # attributes.
    _HINT_PEP484_TYPING_ATTR_NAMES_DEPRECATED: Set[str] = {}

    # If the active Python interpreter targets Python >= 3.9 and thus
    # supports PEP 585, add the names of all deprecated PEP 484-compliant
    # typing attributes (e.g., "typing.List") that have since been obsoleted by
    # equivalent bare PEP 585-compliant builtin classes (e.g., "list").
    if IS_PYTHON_AT_LEAST_3_9:
        _HINT_PEP484_TYPING_ATTR_NAMES_DEPRECATED.update((
            # ..............{ PEP 484                           }..............
            'AbstractSet',
            'AsyncContextManager',
            'AsyncGenerator',
            'AsyncIterable',
            'AsyncIterator',
            'Awaitable',
            'ByteString',
            'Callable',
            'ChainMap',
            'Collection',
            'Container',
            'ContextManager',
            'Coroutine',
            'Counter',
            'DefaultDict',
            'Deque',
            'Dict',
            'FrozenSet',
            'Generator',
            'Hashable',
            'ItemsView',
            'Iterable',
            'Iterator',
            'KeysView',
            'List',
            'MappingView',
            'Mapping',
            'Match',
            'MutableMapping',
            'MutableSequence',
            'MutableSet',
            'OrderedDict',
            'Pattern',
            'Reversible',
            'Sequence',
            'Set',
            'Sized',
            'Tuple',
            'Type',
            'ValuesView',
        ))

    # ..................{ HINTS ~ ignorable                 }..................
    # Set of the unqualified names of all shallowly ignorable typing
    # attributes.
    _HINT_TYPING_ATTR_NAMES_IGNORABLE = {
        # ................{ PEP 484                           }................
        # The "Any" singleton is semantically synonymous with the ignorable
        # PEP-noncompliant "beartype.cave.AnyType" and hence "object" types.
        'Any',

        # The unsubscripted "Optional" singleton semantically expands to the
        # implicit "Optional[Any]" singleton by the same argument. Since PEP
        # 484 also stipulates that all "Optional[t]" singletons semantically
        # expand to "Union[t, type(None)]" singletons for arbitrary arguments
        # "t", "Optional[Any]" semantically expands to merely "Union[Any,
        # type(None)]". Since all unions subscripted by "Any" semantically
        # reduce to merely "Any", the "Optional" singleton also reduces to
        # merely "Any".
        #
        # This intentionally excludes "Optional[type(None)]", which the
        # "typing" module physically reduces to merely "type(None)". *shrug*
        'Optional',

        # The unsubscripted "Union" singleton semantically expands to the
        # implicit "Union[Any]" singleton by the same argument. Since PEP 484
        # stipulates that a union of one type semantically reduces to only that
        # type, "Union[Any]" semantically reduces to merely "Any". Despite
        # their semantic equivalency, however, these objects remain
        # syntactically distinct with respect to object identification: e.g.,
        #     >>> Union is not Union[Any]
        #     True
        #     >>> Union is not Any
        #     True
        #
        # This intentionally excludes:
        #
        # * The "Union[Any]" and "Union[object]" singletons, since the "typing"
        #   module physically reduces:
        #   * "Union[Any]" to merely "Any" (i.e., "Union[Any] is Any"), which
        #     this frozen set already contains.
        #   * "Union[object]" to merely "object" (i.e., "Union[object] is
        #     object"), which this frozen set also already contains.
        # * "Union" singleton subscripted by one or more ignorable type hints
        #   contained in this set (e.g., "Union[Any, bool, str]"). Since there
        #   exist a countably infinite number of these subscriptions, these
        #   subscriptions *CANNOT* be explicitly listed in this set. Instead,
        #   these subscriptions are dynamically detected by the high-level
        #   beartype._util.hint.pep.utilhinttest.is_hint_ignorable() tester
        #   function and thus referred to as deeply ignorable type hints.
        'Union',
    }

    # If the active Python interpreter targets Python 3.6, shallowly ignore the
    # unsubscripted "Generic" superclass whose idiosyncratic representation
    # under Python 3.6 is "typing.Generic" rather than "<class 'Generic'>"".
    # Note that logic above already handles the latter case.
    if IS_PYTHON_3_6:
        _HINT_TYPING_ATTR_NAMES_IGNORABLE.add('Generic')

    # ..................{ HINTS ~ types                     }..................
    # Dictionary mapping from the unqualified name of each classes defined by
    # typing modules uniquely identifying PEP-compliant type hints to their
    # corresponding signs.
    _HINT_TYPE_BASENAMES_TO_SIGN = {
        # ................{ PEP 484                           }................
        # All PEP 484-compliant forward references are necessarily instances of
        # the same class. Unfortunately, this class was only publicized under
        # Python >= 3.7 after its initial privatization under Python <= 3.6.
        ('ForwardRef' if IS_PYTHON_AT_LEAST_3_7 else '_ForwardRef'): (
            HintSignForwardRef),

        # All PEP 484-compliant type variables are necessarily instances of the
        # same class.
        'TypeVar': HintSignTypeVar,

        #FIXME: "Generic" is ignorable when unsubscripted. Excise this up!
        # The unsubscripted PEP 484-compliant "Generic" superclass is
        # explicitly equivalent under PEP 484 to the "Generic[Any]"
        # subscription and thus slightly conveys meaningful semantics.
        # 'Generic': HintSignGeneric,
    }

    # ..................{ CONSTRUCTION                      }..................
    # For the name of each top-level hinting module...
    for typing_module_name in HINT_PEP_MODULE_NAMES:
        # For each deprecated PEP 484-compliant typing attribute name...
        for typing_attr_name in _HINT_PEP484_TYPING_ATTR_NAMES_DEPRECATED:
            # Add that attribute relative to this module to this set.
            HINT_PEP484_BARE_REPRS_DEPRECATED.add(
                f'{typing_module_name}.{typing_attr_name}')

        # For each shallowly ignorable typing attribute name...
        for typing_attr_name in _HINT_TYPING_ATTR_NAMES_IGNORABLE:
            # Add that attribute relative to this module to this set.
            HINT_REPRS_IGNORABLE.add(
                f'{typing_module_name}.{typing_attr_name}')

        # For the name of each sign and that sign...
        for hint_sign_name, hint_sign in datapepsigns.__dict__.items():
            # Unqualified name of the typing attribute identified by this sign.
            typing_attr_name = hint_sign_name[_HINT_SIGN_PREFIX_LEN:]

            # Map from that attribute in this module to this sign.
            HINT_BARE_REPR_TO_SIGN[
                f'{typing_module_name}.{typing_attr_name}'] = hint_sign

        # For the unqualified classname identifying each sign to that sign...
        for hint_type_basename, hint_sign in (
            _HINT_TYPE_BASENAMES_TO_SIGN.items()):
            # Map from that classname in this module to this sign.
            HINT_TYPE_NAME_TO_SIGN[
                f'{typing_module_name}.{hint_type_basename}'] = hint_sign

    # ..................{ SYNTHESIS                         }..................
    # Synthesize the frozen set of all bare deprecated PEP-compliant type hint
    # representations from lower-level PEP-specific sets.
    HINT_BARE_REPRS_DEPRECATED = frozenset(HINT_PEP484_BARE_REPRS_DEPRECATED)

    # Freeze the set of all shallowly ignorable type hint representations.
    HINT_REPRS_IGNORABLE = frozenset(HINT_REPRS_IGNORABLE)

# Initialize this submodule.
_init()