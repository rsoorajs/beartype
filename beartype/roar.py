#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Hear beartype roar** as it handles errors and warnings.

This submodule defines hierarchies of :mod:`beartype`-specific exceptions
and warnings emitted by the :func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from abc import ABCMeta as _ABCMeta

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SUPERCLASS                        }....................
class BeartypeException(Exception, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype exceptions.**

    Instances of subclasses of this exception are raised either:

    * At decoration time from the :func:`beartype.beartype` decorator.
    * At call time from the new callable generated by the
      :func:`beartype.beartype` decorator to wrap the original callable.
    '''

    pass

# ....................{ CAVE                              }....................
class BeartypeCaveException(BeartypeException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype cave exceptions.**

    Instances of subclasses of this exception are raised at usage time from
    various types published by the :func:`beartype.cave` submodule.
    '''

    pass

# ....................{ CAVE ~ NoneTypeOr                 }....................
class BeartypeCaveNoneTypeOrException(
    BeartypeCaveException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype cave** ``None`` **tuple factory
    exceptions.**

    Instances of subclasses of this exception are raised at usage time from
    the :func:`beartype.cave.NoneTypeOr` tuple factory.
    '''

    pass


class BeartypeCaveNoneTypeOrKeyException(BeartypeCaveNoneTypeOrException):
    '''
    **Beartype cave** ``None`` **tuple factory key exception.**

    This exception is raised when indexing the :func:`beartype.cave.NoneTypeOr`
    dictionary with an invalid key, including:

    * The empty tuple.
    * Arbitrary objects that are neither:

      * **Types** (i.e., :class:`beartype.cave.ClassType` instances).
      * **Tuples of types** (i.e., tuples whose items are all
        :class:`beartype.cave.ClassType` instances).
    '''

    pass


class BeartypeCaveNoneTypeOrMutabilityException(
    BeartypeCaveNoneTypeOrException):
    '''
    **Beartype cave** ``None`` **tuple factory mutability exception.**

    This exception is raised when attempting to explicitly set a key on the
    :func:`beartype.cave.NoneTypeOr` dictionary.
    '''

    pass

# ....................{ DECORATOR                         }....................
class BeartypeDecorException(BeartypeException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype decorator exceptions.**

    Instances of subclasses of this exception are raised at decoration time
    from the :func:`beartype.beartype` decorator.
    '''

    pass

# ....................{ DECORATOR ~ wrapp[ee|er]          }....................
class BeartypeDecorWrappeeException(BeartypeDecorException):
    '''
    **Beartype decorator wrappee exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator when passed a **wrappee** (i.e., object
    to be decorated by this decorator) of invalid type.
    '''

    pass


class BeartypeDecorWrapperException(BeartypeDecorException):
    '''
    **Beartype decorator parse exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on accidentally generating an **invalid
    wrapper** (i.e., syntactically invalid new callable to wrap the original
    callable).
    '''

    pass

# ....................{ DECORATOR ~ hint                  }....................
class BeartypeDecorHintException(BeartypeDecorException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype decorator type hint exceptions.**

    Instances of subclasses of this exception are raised at decoration time
    from the :func:`beartype.beartype` decorator on receiving a callable
    annotated by one or more **invalid type hints** (i.e., annotations that are
    neither PEP-compliant nor PEP-compliant type hints supported by this
    decorator).
    '''

    pass


class BeartypeDecorHintForwardRefException(BeartypeDecorHintException):
    '''
    **Beartype decorator forward reference type hint exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on receiving a callable annotated by
    one or more **invalid forward reference type hints** (i.e., strings
    whose values are the names of user-defined classes that have yet to be
    defined).
    '''

    pass


# ....................{ DECORATOR ~ hint : value          }....................
class BeartypeDecorHintNonPepException(BeartypeDecorHintException):
    '''
    **Beartype decorator PEP-noncompliant type hint value exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on receiving a callable type-hinted
    with one or more **PEP-noncompliant annotations** (i.e., annotations that
    fail to comply with :mod:`beartype`-specific semantics, including tuple
    unions and fully-qualified forward references) in a semantic context
    expecting PEP-noncompliant annotations.

    Tuple unions, for example, are required to contain *only* PEP-noncompliant
    annotations. This exception is thus raised for callables type-hinted with
    tuples containing one or more PEP-compliant items (e.g., instances or
    classes declared by the stdlib :mod:`typing` module) *or* arbitrary objects
    (e.g., dictionaries, lists, numbers, sets).
    '''

    pass

# ....................{ DECORATOR ~ hint : pep            }....................
class BeartypeDecorHintPepException(
    BeartypeDecorHintException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype decorator PEP-compliant type hint
    value exceptions.**

    Instances of subclasses of this exception are raised at decoration time
    from the :func:`beartype.beartype` decorator on receiving a callable
    annotated with one or more PEP-compliant type hints either violating an
    annotation-centric PEP (e.g., `PEP 484`_) *or* this decorator's
    implementation of such a PEP.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    pass


class BeartypeDecorHintPepSignException(BeartypeDecorHintPepException):
    '''
    **Beartype decorator PEP-compliant type hint sign exception.**

    Instances of subclasses of this exception are raised at decoration time
    from the :func:`beartype.beartype` decorator on receiving a callable
    annotated with one or more PEP-compliant type hints *not* uniquely
    identifiable by a **sign** (i.e., object uniquely identifying a category
    of PEP-compliant type hints).
    '''

    pass


class BeartypeDecorHintPepUnsupportedException(BeartypeDecorHintPepException):
    '''
    **Beartype decorator unsupported PEP-compliant type hint exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on receiving a callable annotated with
    one or more PEP-compliant type hints (e.g., instances or classes declared
    by the stdlib :mod:`typing` module) currently unsupported by this
    decorator.
    '''

    pass

# ....................{ DECORATOR ~ hint : pep : proposal }....................
class BeartypeDecorHintPep484Exception(BeartypeDecorHintPepException):
    '''
    **Beartype decorator** `PEP 484`_**-compliant type hint value exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on receiving a callable annotated with
    one or more PEP-compliant type hints either violating `PEP 484`_ *or* this
    decorator's implementation of `PEP 484`_, including:

    * Hints subscripted by the :attr:`typing.NoReturn` type hint (e.g.,
      ``typing.List[typing.NoReturn]``).

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    pass


class BeartypeDecorHintPep544Exception(BeartypeDecorHintPepException):
    '''
    **Beartype decorator** `PEP 544`_**-compliant type hint value exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on receiving a callable annotated with
    one or more PEP-compliant type hints either violating `PEP 544`_ *or* this
    decorator's implementation of `PEP 544`_.

    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''

    pass


class BeartypeDecorHintPep585Exception(BeartypeDecorHintPepException):
    '''
    **Beartype decorator** `PEP 585`_**-compliant type hint value exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on receiving a callable annotated with
    one or more PEP-compliant type hints either violating `PEP 585`_ *or* this
    decorator's implementation of `PEP 585`_.

    .. _PEP 585:
       https://www.python.org/dev/peps/pep-0585
    '''

    pass

# ....................{ DECORATOR ~ param                 }....................
class BeartypeDecorParamException(BeartypeDecorException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype decorator parameter exceptions.**

    Instances of subclasses of this exception are raised at decoration time
    from the :func:`beartype.beartype` decorator on receiving a callable
    declaring invalid parameters.
    '''

    pass


class BeartypeDecorParamNameException(BeartypeDecorParamException):
    '''
    **Beartype decorator parameter name exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on receiving a callable declaring
    parameters with **invalid names** (i.e., prefixed by the
    :mod:`beartype`-reserved substring ``"__bear"``).
    '''

    pass

# ....................{ DECORATOR ~ pep                   }....................
class BeartypeDecorPepException(BeartypeDecorException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype decorator Python Enhancement Proposal
    (PEP) exceptions.**

    Instances of subclasses of this exception are raised at decoration time
    from the :func:`beartype.beartype` decorator on receiving a callable
    violating a specific PEP.
    '''

    pass


class BeartypeDecorHintPep563Exception(BeartypeDecorPepException):
    '''
    **Beartype decorator** `PEP 563`_ **evaluation exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator on failing to dynamically evaluate a
    postponed annotation of the decorated callable when `PEP 563`_ is active
    for that callable.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''

    pass

# ....................{ CALL                              }....................
class BeartypeCallException(BeartypeException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartyped callable exceptions.**

    Instances of subclasses of this exception are raised from wrapper functions
    generated by the :func:`beartype.beartype` decorator, typically when
    failing a runtime type-check at call time.
    '''

    pass


class BeartypeCallUnavailableTypeException(BeartypeCallException):
    '''
    **Beartyped callable unavailable type exceptions.**

    This exception is raised from the :class:`beartype.cave.UnavailableType`
    class when passed to either the :func:`isinstance` or :func:`issubclass`
    builtin functions, typically due to a type defined by the
    :class:`beartype.cave` submodule being conditionally unavailable under the
    active Python interpreter.
    '''

    pass

# ....................{ CALL ~ hint                       }....................
class BeartypeCallHintException(BeartypeCallException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartyped callable type-checking exceptions.**

    Instances of subclasses of this exception are raised from wrapper functions
    generated by the :func:`beartype.beartype` decorator when failing a runtime
    type-check at callable call time, typically due to either being passed a
    parameter or returning a value violating a type hint annotating that
    parameter or return value.
    '''

    pass


class BeartypeCallHintForwardRefException(BeartypeCallHintException):
    '''
    **Beartyped callable forward reference type-checking exception.**

    This exception is raised from wrapper functions generated by the
    :func:`beartype.beartype` decorator when a **forward reference type hint**
    (i.e., string whose value is the name of a user-defined class that has yet
    to be defined) erroneously references a module attribute whose value is
    *not* actually a class.
    '''

    pass

# ....................{ CALL ~ hint : pep                 }....................
class BeartypeCallHintPepException(
    BeartypeCallHintException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartyped callable PEP-compliant type
    exceptions.**

    Instances of subclasses of this exception are raised from wrapper functions
    generated by the :func:`beartype.beartype` decorator when either passed a
    parameter or returning an object whose value is of **unexpected
    PEP-compliant type** (i.e., violating a PEP-compliant type hint annotated
    for that parameter or return value).
    '''

    pass


class BeartypeCallHintPepParamException(BeartypeCallHintPepException):
    '''
    **Beartyped callable parameter PEP-compliant type exception.**

    This exception is raised from wrapper functions generated by the
    :func:`beartype.beartype` decorator when passed a parameter whose value is
    of unexpected PEP-compliant type.
    '''

    pass


class BeartypeCallHintPepReturnException(BeartypeCallHintPepException):
    '''
    **Beartyped callable return PEP-compliant type exception.**

    This exception is raised from wrapper functions generated by the
    :func:`beartype.beartype` decorator when returning an object whose value is
    of unexpected PEP-compliant type.
    '''

    pass

# ....................{ CALL ~ hint : nonpep              }....................
class BeartypeCallHintNonPepException(
    BeartypeCallHintException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartyped callable PEP-noncompliant type
    exceptions.**

    Instances of subclasses of this exception are raised from wrapper functions
    generated by the :func:`beartype.beartype` decorator when either passed a
    parameter or returning an object whose value is of **unexpected
    PEP-noncompliant type** (i.e., violating a PEP-noncompliant type hint
    annotated for that parameter or return value).
    '''

    pass


class BeartypeCallHintNonPepParamException(BeartypeCallHintNonPepException):
    '''
    **Beartyped callable parameter PEP-noncompliant type exception.**

    This exception is raised from wrapper functions generated by the
    :func:`beartype.beartype` decorator when passed a parameter whose value is
    of unexpected PEP-noncompliant type.
    '''

    pass


class BeartypeCallHintNonPepReturnException(BeartypeCallHintNonPepException):
    '''
    **Beartyped callable return PEP-noncompliant type exception.**

    This exception is raised from wrapper functions generated by the
    :func:`beartype.beartype` decorator when returning an object whose value is
    of unexpected PEP-noncompliant type.
    '''

    pass

# ....................{ WARNINGS                          }....................
class BeartypeWarning(UserWarning, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype warnings.**

    Instances of subclasses of this warning are emitted either:

    * At decoration time from the :func:`beartype.beartype` decorator.
    * At call time from the new callable generated by the
      :func:`beartype.beartype` decorator to wrap the original callable.
    '''

    pass

# ....................{ WARNINGS ~ decor : hint : pep     }....................
#FIXME: Consider removal.
# class BeartypeDecorHintPepWarning(BeartypeWarning, metaclass=_ABCMeta):
#     '''
#     Abstract base class of all **beartype decorator PEP-compliant type hint
#     warnings.**
#
#     Instances of subclasses of this warning are emitted at decoration time from
#     the :func:`beartype.beartype` decorator on receiving a callable annotated
#     by suspicious (but *not* necessarily erroneous) PEP-compliant type hints
#     warranting non-fatal warnings *without* raising fatal exceptions.
#     '''
#
#     pass


#FIXME: Consider removal.
# class BeartypeDecorHintPepIgnorableDeepWarning(BeartypeDecorHintPepWarning):
#     '''
#     **Beartype decorator deeply ignorable PEP-compliant type hint warning.**
#
#     This warning is emitted at decoration time from the
#     :func:`beartype.beartype` decorator on receiving a callable annotated by
#     one or more **deeply ignorable PEP-compliant type hints** (i.e., instances or classes declared
#     by the stdlib :mod:`typing` module) currently unsupported by this
#     decorator.
#     '''
#
#     pass


#FIXME: Consider removal.
# class BeartypeDecorHintPepUnsupportedWarning(BeartypeWarning):
#     '''
#     **Beartype decorator unsupported PEP-compliant type hint warning.**
#
#     This warning is emitted at decoration time from the
#     :func:`beartype.beartype` decorator on receiving a callable annotated with
#     one or more PEP-compliant type hints (e.g., instances or classes declared
#     by the stdlib :mod:`typing` module) currently unsupported by this
#     decorator.
#     '''
#
#     pass

# ....................{ PRIVATE ~ decorator               }....................
class _BeartypeDecorBeartypistryException(BeartypeDecorException):
    '''
    **Beartype decorator beartypistry exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator when erroneously accessing the
    **beartypistry** (i.e., :class:`beartype._decor._typistry.bear_typistry`
    singleton).

    This private exception denotes a critical internal issue and should thus
    *never* be raised -- let alone exposed to end users.
    '''

    pass

# ....................{ PRIVATE ~ util                    }....................
class _BeartypeUtilException(BeartypeException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype utility exceptions.**

    Instances of subclasses of this exception are raised by *most* (but *not*
    all) private submodules of the private :mod:`beartype._util` subpackage.
    These exceptions denote critical internal issues and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass


class _BeartypeUtilModuleException(_BeartypeUtilException):
    '''
    **Beartype module utility exception.**

    This exception is raised by public functions of the private
    :mod:`beartype._util.py.utilpymodule` subpackage when dynamically importing
    an unimportable external user-defined module, typically due to a
    **PEP-compliant forward reference type hint** (i.e., string whose value is
    the name of a user-defined class that has yet to be defined) erroneously
    referencing a non-existent module or module attribute.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass


class _BeartypeUtilTextException(_BeartypeUtilException):
    '''
    **Beartype text utility exception.**

    This exception is raised by public functions of the private
    :mod:`beartype._util.text` subpackage on various fatal edge cases.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass

# ....................{ PRIVATE ~ util : call               }..................
class _BeartypeCallHintRaiseException(
    _BeartypeUtilException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype human-readable exception raiser
    exceptions.**

    Instances of subclasses of this exception are raised by private utility
    **exception raiser functions** (i.e., functions raising human-readable
    exceptions from wrapper functions when either passed a parameter or
    returning a value annotated by a type hint fails the runtime type-check
    required by that hint) when an unexpected failure occurs.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass

# ....................{ PRIVATE ~ util : call : non-pep     }..................
class _BeartypeCallHintNonPepRaiseException(_BeartypeCallHintRaiseException):
    '''
    **Beartype PEP-noncompliant human-readable exception raiser exception.**

    This exception is raised by the
    :func:`beartype._decor._code._nonpep._nonpeperror.raise_nonpep_call_exception`
    exception raiser function when an unexpected failure occurs.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass

# ....................{ PRIVATE ~ util : call : pep         }..................
class _BeartypeCallHintPepRaiseException(_BeartypeCallHintRaiseException):
    '''
    **Beartype PEP-compliant human-readable exception raiser exception.**

    This exception is raised by the
    :func:`beartype._decor._code._pep._error.peperror.raise_pep_call_exception`
    exception raiser function when an unexpected failure occurs.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass


class _BeartypeCallHintPepRaiseDesynchronizationException(
    _BeartypeCallHintPepRaiseException):
    '''
    **Beartype human-readable exception raiser desynchronization exception.**

    This exception is raised by the
    :func:`beartype._decor._code._pep._error.peperror.raise_pep_call_exception`
    function (which raises human-readable exceptions from wrapper functions
    when either passed a parameter or returning a value, referred to as the
    "pith" for brevity, annotated by a PEP-compliant type hint fails the
    type-check required by that hint) when this pith appears to satisfy this
    type-check, a runtime paradox implying either:

    * The parent wrapper function generated by the :mod:`beartype.beartype`
      decorator type-checking this pith triggered a false negative by
      erroneously misdetecting this pith as failing this type check.
    * The
        :func:`beartype._decor._code._pep._error.peperror.raise_pep_call_exception`
      function re-type-checking this pith triggered a false positive by
      erroneously misdetecting this pith as satisfying this type check when in
      fact this pith fails to do so.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass

# ....................{ PRIVATE ~ util : cache              }..................
class _BeartypeUtilCachedException(_BeartypeUtilException, metaclass=_ABCMeta):
    '''
    Abstract base class of all **beartype caching utility exceptions.**

    Instances of subclasses of this exception are raised by private submodules
    of the private :mod:`beartype._util.cache` subpackage. These exceptions
    denote critical internal issues and should thus *never* be raised -- let
    alone allowed to percolate up the call stack to end users.
    '''

    pass


class _BeartypeUtilCachedCallableException(_BeartypeUtilCachedException):
    '''
    **Beartype memoization exception.**

    This exception is raised by the
    :func:`beartype._util.cache.utilcache.utilcachecall.callable_cached`
    decorator when the signature of the callable being decorated is
    unsupported.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass


class _BeartypeUtilCachedFixedListException(_BeartypeUtilCachedException):
    '''
    **Beartype decorator fixed list exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator when an internal callable erroneously
    mutates a **fixed list** (i.e., list constrained to a fixed length defined
    at instantiation time), usually by attempting to modify the length of that
    list.

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass


class _BeartypeUtilCachedObjectTypedException(_BeartypeUtilCachedException):
    '''
    **Beartype decorator typed object exception.**

    This exception is raised at decoration time from the
    :func:`beartype.beartype` decorator when an internal callable erroneously
    acquires a **pooled typed object** (i.e., object internally cached to a
    pool of all objects of that type).

    This exception denotes a critical internal issue and should thus *never* be
    raised -- let alone allowed to percolate up the call stack to end users.
    '''

    pass
