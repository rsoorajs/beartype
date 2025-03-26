#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint sanitizers** (i.e., high-level callables
converting type hints from one format into another, either permanently or
temporarily and either losslessly or in a lossy manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Optional
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.metadata.metadecor import BeartypeDecorMeta
from beartype._check.metadata.hint.hintsane import (
    HintSane,
    HintSane,
)
from beartype._check.convert._convcoerce import (
    coerce_func_hint_root,
    coerce_hint_any,
    coerce_hint_root,
)
from beartype._check.convert._reduce.redhint import reduce_hint
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.datahinttyping import TypeStack
from beartype._util.cache.map.utilmapbig import CacheUnboundedStrong
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.proposal.pep484585.pep484585func import (
    reduce_hint_pep484585_func_return)

# ....................{ SANIFIERS ~ root                   }....................
#FIXME: Unit test us up, please.
def sanify_hint_root_func(
    # Mandatory parameters.
    decor_meta: BeartypeDecorMeta,
    hint: Hint,
    pith_name: str,

    # Optional parameters.
    arg_kind: Optional[ArgKind] = None,
    exception_prefix: str = EXCEPTION_PLACEHOLDER,
) -> HintSane:
    '''
    Type hint sanified (i.e., sanitized) from the passed **possibly insane root
    type hint** (i.e., possibly PEP-noncompliant hint annotating the parameter
    or return with the passed name of the passed callable) if this hint is both
    reducible and unignorable, this hint unmodified if this hint is both
    irreducible and unignorable, or :obj:`typing.Any` otherwise (i.e., if this
    hint is ignorable).

    Specifically, this function:

    * If this hint is a **PEP-noncompliant tuple union** (i.e., tuple of one or
      more standard classes and forward references to standard classes):

      * Coerces this tuple union into the equivalent :pep:`484`-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this :pep:`484`-compliant union.
      * Returns this :pep:`484`-compliant union.

    * Else if this hint is already PEP-compliant, preserves and returns this
      hint unmodified as is.
    * Else (i.e., if this hint is neither PEP-compliant nor -noncompliant and
      thus invalid as a type hint), raise an exception.

    Caveats
    -------
    This sanifier *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized. Even if this function *could* be
    meaningfully memoized, there would be no benefit; this function is only
    called once per parameter or return of the currently decorated callable.

    This sanifier is intended to be called *after* all possibly
    :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
    evaluatable strings rather than actual type hints) annotating this callable
    if any have been evaluated into actual type hints.

    Parameters
    ----------
    decor_meta : BeartypeDecorMeta
        Decorated callable directly annotated by this hint.
    hint : Hint
        Possibly PEP-noncompliant root type hint to be sanified.
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    arg_kind : Optional[ArgKind]
        Either:

        * If this hint annotates a parameter, that parameter's **kind** (i.e.,
          :class:`.ArgKind` enumeration member conveying the syntactic class of
          that parameter, constraining how the callable declaring that parameter
          requires that parameter to be passed).
        * If this hint annotates the return, :data:`None`.

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Human-readable label prefixing exception messages raised by this
        function. Defaults to :data:`EXCEPTION_PLACEHOLDER`.

    Returns
    -------
    HintSane
        Either:

        * If the passed hint is reducible to:

          * An ignorable lower-level hint, :obj:`typing.Any`.
          * An unignorable lower-level hint, either:

            * If reducing this hint to that lower-level hint generates
              supplementary metadata, that metadata.
            * Else, that lower-level hint alone.

        * Else, this hint is irreducible. In this case, this hint unmodified.

    Raises
    ------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''
    assert isinstance(arg_kind, NoneTypeOr[ArgKind]), (
        f'{repr(arg_kind)} neither argument kind nor "None".')

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the sanify_hint_root_statement() sanitizer.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    #FIXME: This attempt at mutating the "__annotations__" dunder dictionary is
    #likely to fail under Python >= 3.13. Contemplate alternatives, please.
    # PEP-compliant type hint coerced from this possibly (i.e., permanently
    # converted in the annotations dunder dictionary of the passed callable)
    # PEP-noncompliant type hint if this hint is coercible *OR* this hint as is
    # otherwise. Since the passed hint is *NOT* necessarily PEP-compliant,
    # perform this coercion *BEFORE* validating this hint to be PEP-compliant.
    hint = decor_meta.func_arg_name_to_hint[pith_name] = coerce_func_hint_root(
        decor_meta=decor_meta,
        hint=hint,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )

    # If this hint annotates the return, then (in order):
    # * If this hint is contextually invalid for this callable (e.g., generator
    #   whose return is not annotated as "Generator[...]"), raise an exception.
    # * If this hint is either PEP 484- or 585-compliant *AND* requires
    #   reduction (e.g., from "Coroutine[None, None, str]" to just "str"),
    #   reduce this hint accordingly.
    #
    # Perform this reduction *BEFORE* performing subsequent tests (e.g., to
    # accept "Coroutine[None, None, typing.NoReturn]" as expected). Note that
    # this logic *ONLY* pertains to callables (rather than statements) and is
    # thus *NOT* performed by the sanify_hint_root_statement() sanitizer.
    if pith_name == ARG_NAME_RETURN:
        hint = reduce_hint_pep484585_func_return(
            func=decor_meta.func_wrappee,
            func_arg_name_to_hint=decor_meta.func_arg_name_to_hint,
            exception_prefix=exception_prefix,
        )
    # Else, this hint annotates a parameter.

    # Sane child hint reduced from this possibly insane child hint if reducing
    # this hint did not generate supplementary metadata *OR* that metadata
    # otherwise (i.e., if reducing this hint generated supplementary metadata).
    # Reductions simplify subsequent logic elsewhere by transparently converting
    # non-trivial hints (e.g., numpy.typing.NDArray[...]) into semantically
    # equivalent trivial hints (e.g., beartype validators).
    #
    # Whereas the above coercion permanently persists for the duration of the
    # active Python process (i.e., by replacing the original type hint in the
    # annotations dunder dictionary of this callable), this reduction only
    # temporarily persists for the duration of the current call stack. Why?
    # Because hints explicitly coerced above are assumed to be either:
    # * PEP-noncompliant and thus harmful (in the general sense).
    # * PEP-compliant but semantically deficient and thus equally harmful (in
    #   the general sense).
    #
    # In either case, coerced type hints are generally harmful in *ALL* possible
    # contexts for *ALL* possible consumers (including other competing runtime
    # type-checkers). Reduced type hints, however, are *NOT* harmful in any
    # sense whatsoever; they're simply non-trivial for @beartype to support in
    # their current form and thus temporarily reduced in-memory into a more
    # convenient form for beartype-specific type-checking elsewhere.
    hint_or_sane = reduce_hint(
        hint=hint,
        conf=decor_meta.conf,
        decor_meta=decor_meta,
        arg_kind=arg_kind,
        cls_stack=decor_meta.cls_stack,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )

    # Return this hint if this hint is unignorable *OR* "typing.Any" otherwise.
    return hint_or_sane


#FIXME: Unit test us up, please.
def sanify_hint_root_statement(
    hint: Hint,
    conf: BeartypeConf,
    exception_prefix: str,
) -> HintSane:
    '''
    PEP-compliant type hint sanified (i.e., sanitized) from the passed **root
    type hint** (i.e., possibly PEP-noncompliant type hint that has *no* parent
    type hint) if this hint is both reducible and unignorable, this hint
    unmodified if this hint is both irreducible and unignorable, or
    :obj:`typing.Any` otherwise (i.e., if this hint is ignorable).

    This sanifier is principally intended to be called by a **statement-level
    type-checker factory** (i.e., a function creating and returning a runtime
    type-checker type-checking this hint, outside the context of any standard
    type hinting annotation like a user-defined class variable, callable
    parameter or return, or assignment statement). Such factories include:

    * The private :func:`beartype._check.checkmake.make_func_tester` factory,
      internally called by:

      * The public :func:`beartype.door.is_bearable` function.
      * The public :meth:`beartype.door.TypeHint.is_bearable` method.

    Parameters
    ----------
    hint : Hint
        Possibly PEP-noncompliant root type hint to be sanified.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    -------
    HintSane
        Either:

        * If the passed hint is reducible to:

          * An ignorable lower-level hint, :obj:`typing.Any`.
          * An unignorable lower-level hint, either:

            * If reducing this hint to that lower-level hint generates
              supplementary metadata, that metadata.
            * Else, that lower-level hint alone.

        * Else, this hint is irreducible. In this case, this hint unmodified.

    Raises
    ------
    BeartypeDecorHintNonpepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.

    See Also
    --------
    :func:`.sanify_hint_root_func`
        Further details.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the sanify_hint_root_func() sanitizer, please.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # PEP-compliant type hint coerced from this possibly PEP-noncompliant type
    # hint if this hint is coercible *OR* this hint as is otherwise. Since the
    # passed hint is *NOT* necessarily PEP-compliant, perform this coercion
    # *BEFORE* validating this hint to be PEP-compliant.
    hint = coerce_hint_root(hint=hint, exception_prefix=exception_prefix)

    # Sane child hint reduced from this possibly insane child hint if reducing
    # this hint did not generate supplementary metadata *OR* that metadata
    # otherwise (i.e., if reducing this hint generated supplementary metadata).
    # See also sanify_hint_root_func().
    hint_or_sane = reduce_hint(
        hint=hint, conf=conf, exception_prefix=exception_prefix)

    # Return this hint if this hint is unignorable *OR* "typing.Any" otherwise.
    return hint_or_sane

# ....................{ SANIFIERS ~ any                    }....................
#FIXME: Unit test us up, please.
def sanify_hint_child(
    # Mandatory parameters.
    hint: Hint,
    parent_hint_sane: HintSane,

    # Optional parameters.
    cls_stack: TypeStack = None,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    pith_name: Optional[str] = None,
    exception_prefix: str = '',
) -> HintSane:
    '''
    Type hint sanified (i.e., sanitized) from the passed **possibly insane child
    type hint** (i.e., possibly PEP-noncompliant hint transitively subscripting
    the root type hint annotating a parameter or return of the currently
    decorated callable) if this hint is both reducible and unignorable, this
    hint unmodified if this hint is both irreducible and unignorable, or
    :obj:`typing.Any` otherwise (i.e., if this hint is ignorable).

    Parameters
    ----------
    hint : Hint
        Child type hint to be sanified.
    parent_hint_sane : HintSane
        **Sanified parent type hint metadata** (i.e., immutable and thus
        hashable object encapsulating *all* metadata previously returned by
        :mod:`beartype._check.convert.convsanify` sanifiers after sanitizing
        the possibly PEP-noncompliant parent hint of this child hint into a
        fully PEP-compliant parent hint).
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to :obj:`.BEARTYPE_CONF_DEFAULT`, the default beartype configuration.
    pith_name : Optional[str]
        Either:

        * If this hint directly annotates a callable parameter (as the root type
          hint of that parameter), the name of this parameter.
        * If this hint directly annotates a callable return (as the root type
          hint of that return), the magic string ``"return"``.
        * Else, :data:`None`.

        Note that:

        * This parameter should only be passed during exception raising (i.e.,
          from within the :func:`beartype._check.error` subpackage).
        * This parameter should *never* be passed during code generation (i.e.,
          by the :func:`beartype._check.code.codemain.make_check_expr` code
          factory).

        Defaults to :data:`None`.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    HintSane
        Either:

        * If the passed hint is reducible to:

          * An ignorable lower-level hint, :obj:`typing.Any`.
          * An unignorable lower-level hint, either:

            * If reducing this hint to that lower-level hint generates
              supplementary metadata, that metadata.
            * Else, that lower-level hint alone.

        * Else, this hint is irreducible. In this case, this hint unmodified.
    '''
    # print(f'Sanifying child hint {repr(hint)} with type variable lookup table {repr(typevar_to_hint)}...')

    # This sanifier covers the proper subset of logic performed by the
    # sanify_hint_root_statement() sanifier applicable to child type hints.

    #FIXME: *FASCINATING.* Looks like this should now be performed as a
    #preliminary reduction directly inside the reduce_hint() function now. Why?
    #Because reducers recursively call the reduce_hint_child() function. Each
    #time that occurs, this coercion should occur first. Currently, that isn't
    #happening, because this coercion is being performed here outside of the
    #reduce_hint() workflow. In short:
    #* Shift this call to coerce_hint_any() directly inside the body of the
    #  reduce_hint() function.
    #FIXME: *WAIT*. No. We've considered everything extensively. Indeed, the
    #current approach here is the correct approach. What isn't correct,
    #actually, is the reduce_hint_child() function -- which should probably
    #simply call this coerce_hint_any() function. Trivial. *shrug*

    # PEP-compliant hint coerced (i.e., permanently converted in the annotations
    # dictionary of the passed callable) from this possibly PEP-noncompliant
    # hint if this hint is coercible *OR* this hint as is otherwise. Since the
    # passed hint is *NOT* necessarily PEP-compliant, perform this coercion
    # *BEFORE* validating this hint to be PEP-compliant.
    hint = coerce_hint_any(hint)

    # Sane child hint sanified from this possibly insane child hint if reducing
    # this hint did not generate supplementary metadata *OR* that metadata
    # otherwise (i.e., if reducing this hint generated supplementary metadata).
    hint_or_sane = reduce_hint(
        hint=hint,
        parent_hint_sane=parent_hint_sane,
        conf=conf,
        cls_stack=cls_stack,
        pith_name=pith_name,
        exception_prefix=exception_prefix,
    )
    # print(f'[sanify] Detecting hint {repr(hint)} reduction {repr(hint_or_sane)} ignorability...')

    # Return this hint if this hint is unignorable *OR* "Any" otherwise.
    return hint_or_sane
