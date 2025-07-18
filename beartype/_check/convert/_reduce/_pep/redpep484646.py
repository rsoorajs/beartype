#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- or :pep:`646`-compliant **type parameter reducers**
(i.e., low-level callables converting arbitrary hints parametrized by zero or
more :pep:`484`-compliant type variables and/or :pep:`646`-compliant type
variable tuples to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep484612646Exception,
    BeartypeDecorHintPep484TypeVarViolation,
)
from beartype.typing import (
    Optional,
)
from beartype._check.metadata.hint.hintsane import (
    HintOrSane,
    HintSane,
)
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.typing.datatypingport import (
    Hint,
    Pep484646TypeArgToHint,
    TupleHints,
)
from beartype._data.typing.datatyping import (
    TuplePep484646TypeArgs,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.pep.clspep3119 import is_object_issubclassable
from beartype._util.error.utilerrraise import reraise_exception_placeholder
from beartype._util.hint.nonpep.utilnonpeptest import is_hint_nonpep_type
from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
    get_hint_pep484_typevar_bound_or_none,
    is_hint_pep484_typevar,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin,
    get_hint_pep_typeargs,
)
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.kind.map.utilmapfrozen import FrozenDict

# ....................{ REDUCERS                           }....................
#FIXME: Obsolete reduce_hint_pep484_subbed_typevars_to_hints() in favour of this
#more generic alternative, please. *sigh*
def reduce_hint_pep484646_subbed_typeargs_to_hints(
    # Mandatory parameters.
    hint: Hint,

    # Optional parameters.
    hint_parent_sane: Optional[HintSane] = None,
    exception_prefix: str = '',
) -> HintOrSane:
    '''
    Reduce the passed **subscripted hint** (i.e., derivative hint produced by
    subscripting an unsubscripted hint originally parametrized by one or more
    **type parameters** (i.e., :pep:`484`-compliant type variables or
    :pep:`646`-compliant type variable tuples) with one or more child hints) to
    that unsubscripted hint and corresponding **type parameter lookup table**
    (i.e., immutable dictionary mapping from those same type parameters to those
    same child hints).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Caveats
    -------
    This reducer does *not* validate these type parameters to actually be type
    parameters. Instead, this function defers that validation to the caller.
    Why? Efficiency, mostly. Avoiding the need to explicitly validate these type
    parameters reduces the underlying mapping operation to a fast one-liner.

    Let:

    * ``hints_typearg`` be the tuple of the zero or more type parameters
      parametrizing the unsubscripted hint underlying the passed subscripted
      hint.
    * ``hints_child`` be the tuple of the zero or more child hints subscripting
      the passed subscripted hint.

    Then this reducer validates the sizes of these tuple to be constrained as:

    .. code-block:: python

       len(hints_typearg) >= len(hints_child) > 0

    Equally, the passed hint *must* be subscripted by at least one child hint.
    For each such child hint, the unsubscripted hint originating this
    subscripted hint *must* be parametrized by a corresponding type parameter.
    The converse is *not* the case, as:

    * For the first type parameter, there also *must* exist a corresponding
      child hint to map to that type parameter.
    * For *all* type parameters following the first, there need *not* exist a
      corresponding child hint to map to that type parameter. Type parameters
      with *no* corresponding child hints are simply silently ignored (i.e.,
      preserved as type parameters rather than mapped to other hints).

    Equivalently:

    * Both of these tuples *must* be **non-empty** (i.e., contain one or more
      items).
    * This tuple of type parameters *must* contain at least as many items as
      this tuple of child hints. Therefore:

      * This tuple of type parameters *may* contain exactly as many items as
        this tuple of child hints.
      * This tuple of type parameters *may* contain strictly more items than
        this tuple of child hints.
      * This tuple of type parameters must *not* contain fewer items than this
        tuple of child hints.

    Parameters
    ----------
    hint : Hint
        Subscripted hint to be inspected.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convmain` sanifiers after
          sanitizing the possibly PEP-noncompliant parent hint of this child
          hint into a fully PEP-compliant parent hint).

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    HintOrSane
        Either:

        * If the unsubscripted hint (e.g., :class:`typing.Generic`) originating
          this subscripted hint (e.g., ``typing.Generic[S, T]``) is
          unparametrized by type parameters, that unsubscripted hint as is.
        * Else, that unsubscripted hint is parametrized by one or more type
          parameters. In this case, the **sanified type hint metadata** (i.e.,
          :class:`.HintSane` object) describing this reduction.

    Raises
    ------
    exception_cls
        If this type hint is unsubscripted.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type parameters.
    '''

    # ....................{ LOCALS                         }....................
    # Unsubscripted type alias originating this subscripted hint.
    hint_unsubbed = get_hint_pep_origin(
        hint=hint,
        exception_cls=BeartypeDecorHintPep484612646Exception,
        exception_prefix=exception_prefix,
    )

    # Tuple of all type parameters parametrizing this unsubscripted hint.
    #
    # Note that PEP 695-compliant "type" alias syntax superficially appears to
    # erroneously permit type aliases to be parametrized by non-type parameters.
    # In truth, "type" syntax simply permits type aliases to be parametrized by
    # type parameters that ambiguously share the same names as builtin types --
    # which then silently shadow those types for the duration of those aliases:
    #     >>> type muh_alias[int] = float | complex  # <-- *gulp*
    #     >>> muh_alias.__parameters__
    #     (int,)  # <-- doesn't look good so far
    #     >>> muh_alias.__parameters__[0] is int
    #     False  # <-- something good finally happened
    hint_unsubbed_typeargs = get_hint_pep_typeargs(hint_unsubbed)

    # Tuple of all child hints subscripting this subscripted hint.
    hint_childs = get_hint_pep_args(hint)
    # print(f'hint_childs: {repr(hint_childs)}')

    # ....................{ REDUCE                         }....................
    # Decide the type parameter lookup table for this hint. Specifically, reduce
    # this subscripted hint to:
    # * The semantically useful unsubscripted hint originating this semantically
    #   useless subscripted hint.
    # * The type parameter lookup table mapping all type parameters parametrizing
    #   this unsubscripted hint to all non-type parameter hints subscripting
    #   this subscripted hint.

    # ....................{ REDUCE ~ noop                  }....................
    # If either...
    if (
        # This unsubscripted hint is parametrized by no type parameters *OR*...
        #
        # In this case, *NO* type parameter lookup table can be produced by this
        # reduction. Note this is an uncommon edge case. Examples include:
        # * Parametrizations of the PEP 484-compliant "typing.Generic"
        #   superclass (e.g., "typing.Generic[S, T]"). In this case, the
        #   original unsubscripted "typing.Generic" superclass remains
        #   unparametrized despite that superclass later being parametrized.
        not hint_unsubbed_typeargs or
        # This unsubscripted hint is parametrized by the exact same type
        # parameters as this subscripted hint is subscripted by, in which case
        # the resulting type parameter lookup table would uselessly be the
        # identity mapping from each of these type parameters to itself. While
        # an identity type parameter lookup table could trivially be produced,
        # doing so would convey *NO* meaningful semantics and thus be pointless.
        hint_childs == hint_unsubbed_typeargs
    # Then reduce this subscripted hint to simply this unsubscripted hint, as
    # type parameter lookup tables are then irrelevant.
    ):
        return hint_unsubbed
    # Else, this unsubscripted hint is parametrized by one or more type
    # parameters. In this case, produce a type parameter lookup table mapping
    # these type parameters to child hints subscripting this subscripted hint.

    # ....................{ REDUCE ~ map                   }....................
    # Attempt to...
    try:
        # Type parameter lookup table mapping from each of these type parameters
        # to each of these corresponding child hints.
        #
        # Note that we pass parameters positionally due to memoization.
        typearg_to_hint = _get_hint_pep484646_typeargs_to_hints(
            hint, hint_unsubbed_typeargs, hint_childs)
    # print(f'Mapped hint {hint} to type parameter lookup table {typearg_to_hint}!')
    # If doing so raises *ANY* exception, reraise this exception with each
    # placeholder substring (i.e., "EXCEPTION_PLACEHOLDER" instance) replaced by
    # an explanatory prefix.
    except Exception as exception:
        reraise_exception_placeholder(
            exception=exception, target_str=exception_prefix)

    # ....................{ REDUCE ~ composite             }....................
    # Sanified metadata to be returned.
    hint_sane: HintSane = None  # type: ignore[assignment]

    # If this hint has *NO* parent, this is a root hint. In this case...
    if hint_parent_sane is None:
        # Metadata encapsulating this hint and type parameter lookup table.
        hint_sane = HintSane(
            hint=hint_unsubbed, typearg_to_hint=typearg_to_hint)
    # Else, this hint has a parent. In this case...
    else:
        # If the parent hint is also associated with a type parameter lookup
        # table...
        if hint_parent_sane.typearg_to_hint:
            # Full type parameter lookup table merging the table associated this
            # parent hint with the table just decided above for this child hint,
            # efficiently defined as...
            typearg_to_hint = (
                # The type parameter lookup table describing all transitive
                # parent hints of this hint with...
                hint_parent_sane.typearg_to_hint |  # type: ignore[operator]
                # The type parameter lookup table describing this hint.
                #
                # Note that this table is intentionally the second rather than
                # first operand of this "|" operation, efficiently ensuring that
                # type parameters mapped by this hint take precedence over type
                # parameters mapped by transitive parent hints of this hint.
                typearg_to_hint
            )
        # Else, the parent hint is associated with *NO* such table.

        # Metadata encapsulating this hint and type parameter lookup table,
        # while "cascading" any other metadata associated with this parent hint
        # (e.g., recursable hint IDs) down onto this child hint as well.
        hint_sane = hint_parent_sane.permute_sane(
            hint=hint_unsubbed, typearg_to_hint=typearg_to_hint)

    # ....................{ RETURN                         }....................
    # print(f'Reduced subscripted hint {repr(hint)} to unsubscripted hint metadata {repr(hint_sane)}.')

    # Return this metadata.
    return hint_sane

# ....................{ PRIVATE ~ constants                }....................
#FIXME: Currently unneeded, but probably needed someday. Preserve the present
#for the security of the future.
# _TYPEARG_RECURSABLE_DEPTH_MAX = 0
# '''
# Value of the optional ``hint_recursable_depth_max`` parameter passed to the
# :func:`.is_hint_recursive` tester by the :func:`.reduce_hint_pep484_typevar`
# reducer.
#
# This depth ensures that :pep:`484`- or :pep:`646`-compliant type parameters are
# considered to be recursive *only* after having been recursed into at most this
# many times before (i.e., *only* after having been visited exactly once as a
# child hint of an arbitrary parent hint). By definition, type parameters are
# guaranteed to *never* be parent hints. Ergo, recursing into type parameters
# exactly once suffices to expand exactly one nesting level of non-trivial
# recursive data structures. This mirrors the restrained recursion allowed by
# other reducers.
#
# Consider :pep:`695`-compliant type aliases, for example. Unlike type parameters,
# type aliases are guaranteed to *always* be parent hints. The value of the
# optional ``hint_recursable_depth_max`` parameter passed to the
# :func:`.is_hint_recursive` tester by :pep:`695`-specific reducers is thus one
# greater than the value of this global. Nonetheless, the real-world effect is
# exactly the same: exactly one nesting level of type aliases is expanded.
#
# Consider the following :pep:`484`-compliant generic recursively subscripted by
# itself via a :pep:`484`-compliant type variable ``T``:
#
# .. code-block:: python
#
#    class GenericList[T](): ...
#    RecursiveGenericList = GenericList[GenericList]
#
# Instances of this generic satisfying the type hint ``RecursiveGenericList``
# contain an arbitrary number of other instances of this generic, exhibiting this
# internal structure:
#
# .. code-block:: python
#
#    recursive_generic_list = GenericList()
#    recursive_generic_list.append(recursive_generic_list)
#
# Halting recursion at the first expansion of the type parameter ``T`` then
# reduces the type hint ``RecursiveGenericList`` to
# ``GenericList[GenericList[T]]``, , which reduces to
# ``GenericList[GenericList[HINT_SANE_RECURSIVE]]``, , which reduces to
# ``GenericList[GenericList]`` -- conveying exactly one layer of the internal
# semantics of this recursive data structure.
# '''

# ....................{ PRIVATE ~ getters                  }....................
@callable_cached
def _get_hint_pep484646_typeargs_to_hints(
    hint: Hint,
    hint_child_typeargs: TuplePep484646TypeArgs,
    hint_child_hints: TupleHints,
) -> Pep484646TypeArgToHint:
    '''
    Type parameter lookup table mapping from the passed :pep:`484`- or
    :pep:`646`-compliant **type parameters** (i.e., :pep:`484`-compliant type
    variables or :pep:`646`-compliant type variable tuples) to the associated
    passed type hints as key-value pairs of this table.

    This getter is memoized for efficiency. Notably, this getter creates and
    returns a dictionary mapping each type parameter in the passed tuple of type
    parameters to the associated type hint in the passed tuple of type hints
    with the same 0-based tuple index as that type parameter.

    Parameters
    ----------
    hint: Hint
        Parent hint presumably both subscripted by these child hints. This
        parent hint is currently only used to generate human-readable exception
        messages in the event of fatal errors.
    hint_child_typeargs : TuplePep484646TypeArgs
        Tuple of one or more child type parameters originally subscripting the
        origin underlying this parent hint.
    hint_child_hints : TupleHints
        Tuple of one or more child type hints subscripting this parent hint,
        which those type parameters map to.

    Returns
    -------
    Pep484646TypeArgToHint
        Type parameter lookup table mapping these type parameters to these child
        hints.

    Raises
    ------
    BeartypeDecorHintPep484646TypeArgException
        If either:

        * This tuple of type parameters is empty.
        * This tuple of type hints is empty.
        * This tuple of type hints contains more items than this tuple of type
          parameters.
    BeartypeDecorHintPep484TypeVarViolation
        If one of these type hints violates the bounds or constraints of one of
        these type parameters.
    '''
    assert isinstance(hint_child_typeargs, tuple), (
        f'{repr(hint_child_typeargs)} not tuple.')
    assert isinstance(hint_child_hints, tuple), (
        f'{repr(hint_child_hints)} not tuple.')

    # ....................{ PREAMBLE                       }....................
    # If *NO* type parameters were passed, raise an exception.
    if not hint_child_typeargs:
        raise BeartypeDecorHintPep484612646Exception(
            f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
            f'parametrized by no PEP 484 type parameters.'
        )
    # Else, one or more type parameters were passed.
    #
    # If *NO* type hint_child_hints were passed, raise an exception.
    elif not hint_child_hints:
        raise BeartypeDecorHintPep484612646Exception(
            f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
            f'subscripted by no type hints.'
        )
    # Else, one or more type hint_child_hints were passed.
    #
    # If more type hints than type parameters were passed, raise an exception.
    elif len(hint_child_hints) > len(hint_child_typeargs):
        raise BeartypeDecorHintPep484612646Exception(
            f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
            f'number of subscripted type hints {len(hint_child_hints)} exceeds '
            f'number of parametrized type parameters {len(hint_child_typeargs)} '
            f'(i.e., {len(hint_child_hints)} > {len(hint_child_typeargs)}).'
        )
    # Else, either the same number of type hints and type parameters were passed
    # *OR* more type parameters than type hints were passed.

    # ....................{ MAP                            }....................
    # Type parameter lookup table to be returned.
    typearg_to_hint: Pep484646TypeArgToHint = {}

    #FIXME: Optimize into a "while" loop at some point. *sigh*
    # For each passed type parameter and corresponding type hint...
    #
    # Note that:
    # * The C-based zip() builtin has been profiled to be the fastest means of
    #   iterating pairs in pure-Python, interestingly.
    # * If more type parameters than type hints were passed, zip() silently
    #   ignores type parameters with *NO* corresponding type hints -- exactly as
    #   required and documented by the above docstring.
    # print(f'Mapping hint_child_typeargs {hint_child_typeargs} -> hint_child_hints {hint_child_hints}...')
    for hint_child_typearg, hint_child_hint in zip(
        hint_child_typeargs, hint_child_hints):
        # print(f'Mapping typearg {typearg} -> hint {hint}...')
        # print(f'is_hint_nonpep_type({hint})? {is_hint_nonpep_type(hint, False)}')

        #FIXME: Generalize to call a is_hint_pep484646_typearg() tester instead,
        #please. Of course, we're unsure whether that tester even exists. *sigh*
        # If this type parameter is *NOT* actually a type parameter, raise an
        # exception.
        #
        # Note that this should *NEVER* occur. Python itself syntactically
        # guarantees *ALL* child hints parametrizing a PEP-compliant subscripted
        # hint to actually be type parameters. Nonetheless, the caller is under
        # no such constraints. To guard against dev bitrot, we validate this.
        if not is_hint_pep484_typevar(hint_child_typearg):  # pragma: no cover
            raise BeartypeDecorHintPep484612646Exception(
                f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
                f'parametrization {repr(hint_child_typearg)} not '
                f'type parameter (i.e., '
                f'PEP 484 type variable or '
                f'PEP 646 type variable tuple).'
            )
        # Else, this type parameter is actually a type parameter.

        #FIXME: Insufficient. Ideally, we would also validate this hint to be a
        #*SUBHINT* of this type parameter. Specifically, if this type parameter
        #is bounded by one or more bounded constraints, then we should validate
        #this hint to be a *SUBHINT* of those constraints: e.g.,
        #    class MuhClass(object): pass
        #
        #    # PEP 695 type alias parametrized by a type parameter bound to a
        #    # subclass of the "MuhClass" type.
        #    type muh_alias[T: MuhClass] = T | int
        #
        #    # *INVALID.* Ideally, @beartype should reject this, as "int" is
        #    # *NOT* a subhint of "MuhClass".
        #    def muh_func(muh_arg: muh_alias[int]) -> None: pass
        #
        #Doing so is complicated, however, by forward reference proxies. For
        #obvious reasons, forward reference proxies are *NOT* safely resolvable
        #at this early decoration time that this function is typically called
        #at. If this hint either:
        #* Is itself a forward reference proxy, ignore rather than validate this
        #  hint as a subhint of these bounded constraints. Doing so is trivial
        #  by simply calling "is_beartype_forwardref(hint)" here.
        #* Is *NOT* itself a forward reference proxy but is transitively
        #  subscripted by one or more forward reference proxies, ignore rather
        #  than validate this hint as a subhint of these bounded constraints.
        #  Doing so is *EXTREMELY NON-TRIVIAL.* Indeed, there's *NO* reasonable
        #  way to do so directly here. Rather, we'd probably have to embrace an
        #  EAFP approach: that is, just crudely try to:
        #  * Detect whether this hint is a subhint of these bounded constraints.
        #  * If doing so raises an exception indicative of a forward reference
        #    issue, silently ignore that exception.
        #
        #  Of course, we're unclear what exception type that would even be. Does
        #  the beartype.door.is_subhint() tester even explicitly detect forward
        #  reference issues and raise an appropriate exception type? No idea.
        #  Probably *NOT*, honestly. Interestingly, is_subhint() currently even
        #  fails to support standard PEP 484-compliant forward references:
        #      >>> is_subhint('int', int)
        #      beartype.roar.BeartypeDoorNonpepException: Type hint 'int'
        #      currently unsupported by "beartype.door.TypeHint".
        #
        #Due to these (and probably more) issues, we currently *ONLY* validate
        #this hint to be a subhint of these bounded constraints.

        # If...
        elif (
            # This type parameter is a PEP 484-compliant type variable *AND*...
            is_hint_pep484_typevar(hint_child_typearg) and

            #FIXME: This doesn't particularly belong here. Shift *ALL* of the
            #following logic into a #new check_hint_pep484_typevar() utility
            #function in the
            #"beartype._util.hint.pep.proposal.pep484.pep484typevar" submodule.

            # This hint is a PEP-noncompliant isinstanceable type (and thus
            # *NOT* an unresolvable forward reference proxy, which by definition
            # is *NOT* isinstanceable)...
            is_hint_nonpep_type(
                hint=hint_child_hint, is_forwardref_valid=False)
        ):
            # PEP-compliant type hint synthesized from all bounded constraints
            # parametrizing this type variable if any *OR* "None" otherwise.
            #
            # Note that this call is intentionally passed positional rather
            # positional keywords due to memoization.
            typevar_bound = get_hint_pep484_typevar_bound_or_none(
                hint_child_typearg, EXCEPTION_PLACEHOLDER)
            # print(f'[{typearg}] is_object_issubclassable({typevar_bound})? ...')
            # print(f'{is_object_issubclassable(typevar_bound, False)}')

            # If...
            if (
                # This type variable was bounded or constrained *AND*...
                typevar_bound is not None and
                # These bounded constraints are PEP-noncompliant *AND*...
                #
                # PEP-compliant constraints are *NOT* safely passable to the
                # isinstance() or issubclass() testers, even if they technically
                # are isinstanceable or issubclassable. Why? Consider the
                # "typing.Any" singleton. Under newer Python versions, the
                # "typing.Any" singleton is actually defined as a subclassable
                # type. Although effectively *NO* real-world types subclass
                # "typing.Any", literally *ALL* objects (including types)
                # satisfy the "typing.Any" type hint. Passing "typing.Any" as
                # the second variable to the issubclass() tester below would
                # thus erroneously reject (rather than silently accept) *ALL*
                # objects as unconditionally violating these bounds.
                not is_hint_pep(typevar_bound) and
                # These bounded constraints are issubclassable (i.e., an object
                # safely passable as the second variable to the issubclass()
                # builtin) *AND*...
                #
                # Note that this function is memoized and thus permits *ONLY*
                # positional variables.
                is_object_issubclassable(
                    typevar_bound,
                    # Ignore unresolvable forward reference proxies (i.e.,
                    # beartype-specific objects referring to user-defined
                    # external types that have yet to be defined).
                    False,
                ) and
                # This PEP-noncompliant isinstanceable type hint is *NOT* a
                # subclass of these bounded constraints...
                not issubclass(hint_child_hint, typevar_bound)  # type: ignore[arg-type]
            ):
                # Raise a type-checking violation.
                raise BeartypeDecorHintPep484TypeVarViolation(
                    message=(
                        f'{EXCEPTION_PLACEHOLDER}type hint {repr(hint)} '
                        f'originally parametrized by '
                        f'PEP 484 type variable {repr(hint_child_typearg)} '
                        f'subsequently subscripted by '
                        f'child type hint {repr(hint_child_hint)} violating '
                        f"this type variable's bounds or constraints "
                        f'{repr(typevar_bound)}.'
                    ),
                    culprits=(hint_child_hint,),
                )
            # Else, this type variable was either:
            # * Unbounded and unconstrained.
            # * Bounded or constrained by a hint that is *NOT* issubclassable.
            # * Bounded or constrained by an issubclassable object that is the
            #   superclass of this corresponding hint, which thus satisfies
            #   these bounded constraints.
        # Else, this hint is *NOT* a PEP-noncompliant isinstanceable type.

        # Map this type parameter to this hint with an optimally efficient
        # one-liner, silently overwriting any prior such mapping of this type
        # parameter by either this call or a prior call of this function.
        typearg_to_hint[hint_child_typearg] = hint_child_hint

    # ....................{ RETURN                         }....................
    # Return this table, coerced into an immutable frozen dictionary.
    return FrozenDict(typearg_to_hint)
