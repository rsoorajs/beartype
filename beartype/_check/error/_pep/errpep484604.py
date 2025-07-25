#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`484`-compliant **union type hint violation describers**
(i.e., functions returning human-readable strings explaining violations of
:pep:`484`-compliant union type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._data.hint.sign.datahintsignset import HINT_SIGNS_UNION
from beartype._check.error.errcause import ViolationCause
from beartype._check.metadata.hint.hintsane import HINT_SANE_IGNORABLE
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_origin_type_isinstanceable_or_none)
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.text.utiltextjoin import join_delimited_disjunction_types
from beartype._util.text.utiltextmunge import (
    suffix_str_unless_suffixed,
    uppercase_str_char_first,
)
from beartype._util.text.utiltextrepr import represent_pith

# ....................{ GETTERS                            }....................
def find_cause_pep484604_union(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the PEP-compliant union type hint of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'
    assert cause.hint_sign in HINT_SIGNS_UNION, (
        f'{repr(cause.hint)} not union sign.')
    # print(f'[union] Finding cause for child hints {cause.hint_childs_sane}...')

    # ....................{ LOCALS                         }....................
    # Indentation preceding each line of the strings returned by child getter
    # functions called by this parent getter function, offset to visually
    # demarcate child from parent causes in multiline strings.
    CAUSE_INDENT_CHILD = cause.cause_indent + '  '

    # List of all human-readable strings describing the failure of this pith to
    # satisfy each of these child hints.
    cause_strs = []

    # Subset of all classes shallowly associated with these child hints (i.e.,
    # by being either these child hints in the case of non-"typing" classes
    # *OR* the classes originating these child hints in the case of
    # PEP-compliant type hints) that this pith fails to shallowly satisfy.
    hint_types_violated = set()

    # Truncated object representation of this pith.
    pith_repr = represent_pith(cause.pith)

    # 0-based index of the first non-whitespace character following this
    # representation in violation causes collected below. Look. Just accept it.
    PITH_REPR_INDEX = len(pith_repr) + 1

    # ....................{ SEARCH                         }....................
    # For each subscripted argument of this union...
    for hint_child_sane in cause.hint_childs_sane:
        # If this child hint is ignorable, continue to the next.
        if hint_child_sane is HINT_SANE_IGNORABLE:
            continue
        # Else, this child hint is unignorable.

        # Child hint encapsulated by this metadata.
        hint_child = hint_child_sane.hint

        # If this child hint is PEP-compliant...
        if is_hint_pep(hint_child):
            # Non-"typing" class originating this child hint if any *OR* "None"
            # otherwise.
            hint_child_origin_type = (
                get_hint_pep_origin_type_isinstanceable_or_none(hint_child))

            # If...
            if (
                # This child hint originates from a non-"typing" type *AND*...
                hint_child_origin_type is not None and
                # This pith is *NOT* an instance of this type...
                not isinstance(cause.pith, hint_child_origin_type)
            # Then this pith fails to satisfy this child hint. In this case...
            ):
                # Add this type to the subset of all types this pith violates.
                hint_types_violated.add(hint_child_origin_type)

                # Continue to the next child hint.
                continue
            # Else, this pith is an instance of this type and thus shallowly
            # (but *NOT* necessarily deeply) satisfies this child hint.

            # Child hint output cause to be returned, type-checking only whether
            # this pith deeply satisfies this child hint.
            cause_child = cause.permute_cause(
                hint_sane=hint_child_sane, cause_indent=CAUSE_INDENT_CHILD,
            ).find_cause()

            # If this pith deeply satisfies this child hint, return this cause.
            if cause_child.cause_str_or_none is None:
                # print('Union child {!r} pith {!r} deeply satisfied!'.format(hint_child, pith))
                return cause
            # Else, this pith deeply violates this child hint.

            # Cause of this violation.
            cause_str = cause_child.cause_str_or_none

            # If this cause is prefixed by the truncated object representation
            # of this pith...
            #
            # Note that this should *ALWAYS* be the case. Nonetheless, let's
            # *NOT* assume anything to avoid exploding everything.
            if cause_str.startswith(pith_repr):
                # Strip the prefixing
                # representation of this pith from this cause (e.g., the prefix
                # "MuhClass <object MuhClass at 0x7fbc277a2cf0>" from the cause
                # 'MuhClass <object MuhClass at 0x7fbc277a2cf0> not instance of
                # <protocol "muh_package.MuhProtocol">'). Why? Because the block
                # of text preceding the bulleted list containing this cause is
                # already redundantly prefixed by this representation.
                cause_str = cause_str[PITH_REPR_INDEX:]
            # Else, this cause is *NOT* prefixed by the truncated object
            # representation of this pith. In this case, silently accept that
            # Bad Things have happened and that we should move to a Bad Future.

            # Append the cause of this violation as a bullet-prefixed line to
            # the running list of these lines.
            cause_strs.append(cause_str)
            # print(f'[union] Appended PEP-compliant child hint {hint_child} cause {cause_str}!')
        # Else, this child hint is PEP-noncompliant. In this case...
        else:
            # Assert this child hint to be a non-"typing" class. Note that
            # the "typing" module should have already guaranteed that all
            # subscripted arguments of unions are either PEP-compliant type
            # hints or non-"typing" classes.
            assert isinstance(hint_child, type), (
                f'{cause.exception_prefix}union type hint '
                f'{repr(cause.hint)} child hint {repr(hint_child)} invalid '
                f'(i.e., neither type hint nor non-"typing" class).')
            # Else, this child hint is a non-"typing" type.

            # If this pith is an instance of this type, this pith satisfies this
            # hint. In this case, return this cause as is.
            if isinstance(cause.pith, hint_child):
                return cause
            # Else, this pith is *NOT* an instance of this type, implying this
            # pith to *NOT* satisfy this hint.

            # Add this class to the subset of all types this pith violates.
            hint_types_violated.add(hint_child)
            # print(f'[union] Appended PEP-noncompliant child hint {hint_child}!')

    # ....................{ CAUSE                          }....................
    # If this pith fails to shallowly satisfy one or more of the types of this
    # union, concatenate these failures onto one discrete bullet-prefixed line.
    if hint_types_violated:
        # Human-readable comma-delimited disjunction of the names of these
        # classes (e.g., "bool, float, int, or str").
        cause_types_unsatisfied = join_delimited_disjunction_types(
            types=hint_types_violated, is_color=cause.conf.is_color)

        # Prepend this cause as a discrete bullet-prefixed line.
        #
        # Note that this cause is intentionally prependend rather than appended
        # to this list. Since this cause applies *ONLY* to the shallow type of
        # the current pith rather than any items contained in this pith,
        # listing this shallow cause *BEFORE* other deeper causes typically
        # applying to items contained in this pith produces substantially more
        # human-readable exception messages: e.g.,
        #     # This reads well.
        #     @beartyped pep_hinted() parameter pep_hinted_param=(1,) violates
        #     PEP type hint typing.Union[int, typing.Sequence[str]], as (1,):
        #     * Not int.
        #     * Tuple item 0 value "1" not str.
        #
        #     # This does not.
        #     @beartyped pep_hinted() parameter pep_hinted_param=(1,) violates
        #     PEP type hint typing.Union[int, typing.Sequence[str]], as (1,):
        #     * Tuple item 0 value "1" not str.
        #     * Not int.
        #
        # Note that prepending to lists is an O(n) operation, but that this
        # cost is negligible in this case both due to the negligible number of
        # child hints of the average "typing.Union" in general *AND* due to the
        # fact that this function is only called when a catastrophic type-check
        # failure has already occurred.
        cause_strs.insert(0, f'not {cause_types_unsatisfied}')
    # Else, this pith shallowly satisfies *ALL* the types of this union.

    # If prior logic appended *NO* causes, raise an exception.
    if not cause_strs:
        raise _BeartypeCallHintPepRaiseException(
            f'{cause.exception_prefix}type hint '
            f'{repr(cause.hint)} failure causes unknown.'
        )
    # Else, prior logic appended one or more strings describing these failures.

    # Output cause to be returned, permuted from this input cause such that the
    # output cause justification is either...
    cause_return = cause.permute_cause(cause_str_or_none=(
        # If prior logic appended one cause, a single-line
        # substring intended to be embedded in a longer string;
        f'{pith_repr} {cause_strs[0]}'
        if len(cause_strs) == 1 else
        # Else, prior logic appended two or more causes. In this case, a
        # multiline string comprised of...
        '{}:\n{}'.format(
            # This truncated object representation followed by...
            pith_repr,
            # The newline-delimited concatenation of each cause as a discrete
            # bullet-prefixed line...
            '\n'.join(
                '{}* {}'.format(
                    # Indented by the current indent...
                    cause.cause_indent,
                    # Whose first character is uppercased...
                    uppercase_str_char_first(
                        # Suffixed by a period if not yet suffixed by a period.
                        suffix_str_unless_suffixed(text=cause_str, suffix='.')
                    )
                )
                # '{}* {}.'.format(cause_indent, uppercase_str_char_first(cause_union))
                for cause_str in cause_strs
            )
        )
    ))

    # Return this cause.
    return cause_return
