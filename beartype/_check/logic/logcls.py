#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **hint sign logic class hierarchy** (i.e., dataclasses encapsulating
all low-level Python code snippets and associated metadata required to
dynamically generate high-level Python code snippets fully type-checking various
kinds of type hints uniquely identified by common signs).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta, abstractmethod
from beartype.typing import (
    TYPE_CHECKING,
)
from beartype._check.error.errcause import ViolationCause
from beartype._conf.confenum import BeartypeStrategy
from beartype._data.hint.datahinttyping import (
    CallableStrFormat,
    EnumeratorItem,
    Enumerator,
)
from beartype._data.code.pep.datacodepep484585 import (
    CODE_PEP484585_CONTAINER_ARGS_1_format,
    CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR_format,
    CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format,
)

# ....................{ SUPERCLASSES                       }....................
class HintSignLogicABC(object, metaclass=ABCMeta):
    '''
    Abstract base class (ABC) of all **hint sign logic** (i.e., dataclasses
    encapsulating all low-level Python code snippets and associated metadata
    required to dynamically generate a high-level Python code snippet fully
    type-checking some kind of type hint uniquely identified by a common sign).

    Caveats
    -------
    **Python code snippets should not contain ternary conditionals.** For
    unknown reasons suggesting a critical defect in the current implementation
    of Python 3.8's assignment expressions, snippets containing one or more
    ternary conditionals raise :exc:`UnboundLocalError` exceptions resembling:

        UnboundLocalError: local variable '__beartype_pith_1' referenced before
        assignment

    In particular, the initial draft of these snippets guarded against empty
    sequences with a seemingly reasonable ternary conditional:

    .. code-block:: python

       CODE_PEP484585_SEQUENCE_ARGS_1 = \'\'\'(
       {indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
       {indent_curr}    {hint_child_placeholder} if {pith_curr_var_name} else True
       {indent_curr})\'\'\'

    That should behave as expected, but doesn't, presumably due to obscure
    scoping rules and a non-intuitive implementation of ternary conditionals in
    CPython. Ergo, the current version of this snippet guards against empty
    sequences with disjunctions and conjunctions (i.e., ``or`` and ``and``
    operators) instead. Happily, the current version is more efficient than the
    equivalent approach based on ternary conditional (albeit less intuitive).

    Attributes
    ----------
    code_format : CallableStrFormat
        :meth:`str.format` method bound to a Python code snippet fully
        type-checking the current pith against this kind of type hint. This
        snippet is expected to contain exactly these format variables:

        * ``{indent_curr}``, expanding to the current indentation.
        * ``{pith_curr_assign_expr}``, expanding to an assignment expression
          efficiently yielding the current pith.
        * ``{hint_curr_expr}``, expanding to an arbitrary expression usually
          inefficiently yielding the current pith.
        * ``{pith_curr_var_name}``, expanding to the name of the local variable
          whose value is the current pith.
        * ``{hint_child_placeholder}``, expanding to a Python code snippet
          efficiently type-checking some item of the current pith.
    is_var_random_int_needed : bool
        :data:`True` only if the Python code snippet dynamically generated by
        calling the :attr:`code_format` method requires a pseudo-random integer
        by accessing the local variable named
        :data:`beartype._check.checkmagic.VAR_NAME_RANDOM_INT`. If :data:`True`,
        the body of the current wrapper function will be prefixed by a Python
        statement assigning such an integer to this local.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'code_format',
        'is_var_random_int_needed',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        code_format : CallableStrFormat
        is_var_random_int_needed : bool

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        code_format: CallableStrFormat,

        # Optional parameters.
        is_var_random_int_needed: bool = False,
    ) -> None:
        '''
        Initialize this hint sign logic.

        Parameters
        ----------
        See the class docstring for further details.
        '''

        # Classify all passed parameters.
        self.code_format = code_format
        self.is_var_random_int_needed = is_var_random_int_needed


class HintSignLogicContainerArgs1(HintSignLogicABC):
    '''
    **Single-argument container hint sign logic** (i.e., dataclass encapsulating
    all low-level Python code snippets and associated metadata required to
    dynamically generate a high-level Python code snippet fully type-checking
    some kind of :pep:`484`- or :pep:`585`-compliant container type hint
    uniquely identified by a common sign, satisfying at least the
    :class:`collections.abc.Container` protocol subscripted by exactly one child
    type hint constraining *all* items contained in that container) subclass.

    Attributes
    ----------
    pith_child_expr_format : CallableStrFormat
        :meth:`str.format` method bound to a Python expression efficiently
        yielding the value of the next item (which will then be type-checked)
        contained in the **current pith** (which is the parent container
        currently being type-checked). This snippet is expected to contain
        exactly these format variables:

        * ``{pith_curr_var_name}``, expanding to the name of the local variable
          whose value is the current pith.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'pith_child_expr_format',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        pith_child_expr_format: CallableStrFormat

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self, pith_child_expr_format: CallableStrFormat, **kwargs) -> None:
        '''
        Initialize this hint sign logic.

        Parameters
        ----------
        See the class docstring for further details. All remaining passed
        keyword parameters are passed as is to the superclass
        :meth:`HintSignLogicABC.__init__` method.
        '''

        # Initialize our superclass.
        super().__init__(
            code_format=CODE_PEP484585_CONTAINER_ARGS_1_format, **kwargs)

        # Classify all passed parameters.
        self.pith_child_expr_format = pith_child_expr_format

    # ..................{ ITERATORS                          }..................
    def enumerate_cause_items(self, cause: ViolationCause) -> Enumerator:
        '''
        Arbitrary iterator satisfying the :func:`enumerate` protocol over a
        subset or possibly all items contained in the current pith as configured
        by the beartype configuration of the passed violation cause.

        This configuration configures how many items this iterator enumerates
        over. In particular, if this configuration enables:

        * The default :math:`O1` constant-time type-checking strategy (i.e., if
          ``conf.strategy is beartype.BeartypeStrategy.O1``), this iterator
          efficiently enumerates over only a fixed number of (typically only one
          or two) items of this pith.
        * The :math:`On` linear-time type-checking strategy (i.e., if
          ``conf.strategy is beartype.BeartypeStrategy.On``), this iterator
          inefficiently enumerates over *all* items of this pith.

        Parameters
        ----------
        cause: ViolationCause
            Type-checking violation cause finder to be inspected.

        Returns
        -------
        Enumerator
            Iterator yielding zero or more 2-tuples of the standard form
            ``(item_index, item)``, where:

            * ``item_index`` is the 0-based index of the currently enumerated
              item.
            * ``item`` is an arbitrary item of this pith.
        '''

        # Iterator to be returned.
        container_enumerator: Enumerator = None  # type: ignore[assignment]

        # If the only a single item of this container was type-checked by the
        # parent @beartype-generated wrapper function in O(1) time, type-check
        # only the same single item of this container in O(1) time as well.
        if cause.conf.strategy is BeartypeStrategy.O1:
            # 2-tuple of the index and value of an arbitrary item in the same
            # order as the 2-tuples returned by the enumerate() builtin.
            container_enumerator_item = self._get_cause_enumerator_item(cause)

            # Iterator yielding only this 2-tuple.
            container_enumerator = iter((container_enumerator_item,))
        # Else, *ALL* items of this container were type-checked by the parent
        # @beartype-generated wrapper function in O(n) time. In this case,
        # type-check *ALL* items of this container in O(n) time as well.
        else:
            # Iterator yielding all indices and items of this container.
            container_enumerator = enumerate(cause.pith)

        # Return this iterator.
        return container_enumerator

    # ..................{ PRIVATE ~ getters                  }..................
    @abstractmethod
    def _get_cause_enumerator_item(
        self, cause: ViolationCause) -> EnumeratorItem:
        '''
        2-tuple ``(item_index, item)`` describing an arbitrary item efficiently
        accessed from the passed container, satisfying the format of the items
        yielded by the :func:`enumerate` iterator.

        Parameters
        ----------
        cause: ViolationCause
            Type-checking violation cause finder to be inspected.

        Returns
        -------
        EnumeratorItem
            2-tuple of the standard form ``(item_index, item)`` returned by the
            :func:`enumerate` builtin, where:

            * ``item_index`` is the 0-based index of an arbitrary item
              efficiently accessed from this container.
            * ``item`` is that item.
        '''

        pass

# ....................{ SUBCLASSES ~ container             }....................
class HintSignLogicReiterableArgs1(HintSignLogicContainerArgs1):
    '''
    **Single-argument reiterable hint sign logic** (i.e., dataclass
    encapsulating all low-level Python code snippets and associated metadata
    required to dynamically generate a high-level Python code snippet fully
    type-checking some kind of :pep:`484`- or :pep:`585`-compliant reiterable
    type hint uniquely identified by a common sign, satisfying at least the
    :class:`collections.abc.Collection` protocol subscripted by exactly one
    child type hint constraining *all* items contained in that reiterable)
    subclass.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this hint sign logic.
        '''

        # Initialize our superclass.
        super().__init__(
            pith_child_expr_format=(
                CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR_format),
        )

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_cause_enumerator_item(
        self, cause: ViolationCause) -> EnumeratorItem:

        # First item of this container.
        item = next(iter(cause.pith))

        # 0-based index of this item for readability purposes.
        item_index = 0

        # Return a 2-tuple "(item_index, item)" describing this item.
        return (item_index, item)


class HintSignLogicSequenceArgs1(HintSignLogicContainerArgs1):
    '''
    **Single-argument sequence hint sign logic** (i.e., dataclass encapsulating
    all low-level Python code snippets and associated metadata required to
    dynamically generate a high-level Python code snippet fully type-checking
    some kind of :pep:`484`- or :pep:`585`-compliant sequence type hint
    uniquely identified by a common sign, satisfying at least the
    :class:`collections.abc.Sequence` protocol subscripted by exactly one child
    type hint constraining *all* items contained in that sequence) subclass.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this hint sign logic.
        '''

        # Initialize our superclass.
        super().__init__(
            # Code snippets dynamically generated by this logic require
            # pseudo-random integers to type-check random sequence items.
            is_var_random_int_needed=True,
            pith_child_expr_format=(
                CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format),
        )

    # ..................{ PRIVATE ~ getters                  }..................
    def _get_cause_enumerator_item(
        self, cause: ViolationCause) -> EnumeratorItem:
        assert cause.random_int is not None, (
            f'Violation cause {repr(cause)} pseudo-random integer is "None".')

        # 0-based index of this item calculated from this random integer in the
        # *SAME EXACT WAY* as in the parent @beartype-generated wrapper.
        item_index = cause.random_int % len(cause.pith)

        # Pseudo-random item with this index in this sequence.
        item = cause.pith[item_index]

        # Return a 2-tuple "(item_index, item)" describing this item.
        return (item_index, item)
