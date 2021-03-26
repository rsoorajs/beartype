#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable code object utilities.**

This private submodule implements utility functions dynamically introspecting
**code objects** (i.e., instances of the :class:`CodeType` type)
underlying all pure-Python callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeUtilCallableException
from collections.abc import Callable
from types import CodeType, FrameType, FunctionType, MethodType
from typing import Optional, Union

# ....................{ HINTS                             }....................
CallableOrFrameOrCodeType = Union[Callable, CodeType, FrameType]
'''
PEP-compliant type hint matching either a callable *or* code object.
'''

# ....................{ VALIDATORS                        }....................
def die_unless_func_python(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: type = _BeartypeUtilCallableException
) -> None:
    '''
    Raise an exception if the passed function is **C-based** (i.e., implemented
    in C as either a builtin bundled with the active Python interpreter *or*
    third-party C extension function).

    Equivalently, this validator raises an exception unless the passed function
    is **pure-Python** (i.e., implemented in Python as either a function or
    method).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.
    exception_cls : type, optional
        Type of exception to be raised if this callable is neither a
        pure-Python function nor method. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Raises
    ----------
    exception_cls
         If this callable has *no* code object and is thus *not* pure-Python.
    '''

    # Code object underlying this callable if this callable is pure-Python *OR*
    # "None" otherwise.
    func_codeobj = get_func_codeobj_or_none(func)

    # If this callable is *NOT* pure-Python, raise an exception.
    if func_codeobj is None:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        raise exception_cls(
            f'Callable {repr(func)} code object not found '
            f'(e.g., due to being either C-based or a class or object '
            f'defining the ``__call__()`` dunder method).'
        )
    # Else, this code object exists.

# ....................{ GETTERS                           }....................
def get_func_codeobj(
    # Mandatory parameters.
    func: CallableOrFrameOrCodeType,

    # Optional parameters.
    exception_cls: type = _BeartypeUtilCallableException
) -> CodeType:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed callable if this callable is pure-Python *or* raise an exception
    otherwise (e.g., if this callable is C-based or a class or object defining
    the ``__call__()`` dunder method).

    For convenience, this getter also accepts a code object, in which case that
    code object is simply returned as is.

    Code objects have a docstring under CPython resembling:

    .. _code-block:: python

       Code objects provide these attributes:
           co_argcount         number of arguments (not including *, ** args
                               or keyword only arguments)
           co_code             string of raw compiled bytecode
           co_cellvars         tuple of names of cell variables
           co_consts           tuple of constants used in the bytecode
           co_filename         name of file in which this code object was
                               created
           co_firstlineno      number of first line in Python source code
           co_flags            bitmap: 1=optimized | 2=newlocals | 4=*arg |
                               8=**arg | 16=nested | 32=generator | 64=nofree |
                               128=coroutine | 256=iterable_coroutine |
                               512=async_generator
           co_freevars         tuple of names of free variables
           co_posonlyargcount  number of positional only arguments
           co_kwonlyargcount   number of keyword only arguments (not including
                               ** arg)
           co_lnotab           encoded mapping of line numbers to bytecode
                               indices
           co_name             name with which this code object was defined
           co_names            tuple of names of local variables
           co_nlocals          number of local variables
           co_stacksize        virtual machine stack space required
           co_varnames         tuple of names of arguments and local variables

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Callable or frame or code object to be inspected.
    exception_cls : type, optional
        Type of exception to be raised if this callable is neither a
        pure-Python function nor method. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    CodeType
        Code object underlying this callable.

    Raises
    ----------
    exception_cls
         If this callable has *no* code object and is thus *not* pure-Python.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #FIXME: Synchronize this logic with get_func_codeobj_or_none().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # If the passed object is already a code object, return this object as is.
    if isinstance(func, CodeType):
        return func
    # Else, this object is *NOT* already a code object.
    #
    # If this object is a call stack frame, return this frame's code object.
    elif isinstance(func, FrameType):
        return func.f_code
    # Else, this object is *NOT* a call stack frame and is thus a callable.

    # Code object underlying this callable if this callable is pure-Python *OR*
    # "None" otherwise.
    func_codeobj = get_func_codeobj_or_none(func)

    # If this callable is *NOT* pure-Python, raise an exception.
    if func_codeobj is None:
        die_unless_func_python(func=func, exception_cls=exception_cls)
    # Else, this callable is pure-Python and this code object exists.

    # Return this code object.
    return func_codeobj  # type: ignore[return-value]


def get_func_codeobj_or_none(
    func: CallableOrFrameOrCodeType) -> Optional[CodeType]:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed callable if this callable is pure-Python *or* ``None`` otherwise
    (e.g., if this callable is C-based or a class or object defining the
    ``__call__()`` dunder method).

    Parameters
    ----------
    func : CallableOrFrameOrCodeType
        Callable or frame or code object to be inspected.

    Returns
    ----------
    Optional[CodeType]
        Either:

        * If this callable is pure-Python, this callable's code object.
        * Else, ``None``.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #FIXME: Synchronize this logic with get_func_codeobj().
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # If the passed object is already a code object, return this object as is.
    if isinstance(func, CodeType):
        return func
    # Else, this object is *NOT* already a code object.
    #
    # If this object is a call stack frame, return this frame's code object.
    elif isinstance(func, FrameType):
        return func.f_code

    # Else, this object is *NOT* a call stack frame and is thus a callable.
    # If this callable is a pure-Python bound method, reduce this callable to
    # the pure-Python unbound function encapsulated by this method.
    #
    # Note that this test intentionally leverages the stdlib
    # "types.MethodType" class rather than our equivalent
    # "beartype.cave.MethodBoundInstanceOrClassType" class to avoid circular
    # import issues.
    if isinstance(func, MethodType):
        func = func.__func__
    # Else, this callable is *NOT* a pure-Python bound method.
    #
    # In either case, this callable is now a pure-Python unbound function.

    # Return either...
    #
    # Note that the equivalent could also technically be written as
    # "getattr(func, '__code__', None)", but that doing so would both be less
    # efficient *AND* render this getter less robust. Why? Because the
    # getattr() builtin internally calls the __getattr__() and
    # __getattribute__() dunder methods, either of which could raise arbitrary
    # exceptions, and is thus considerably less safe.
    #
    # Note that this test intentionally leverages the stdlib
    # "types.FunctionType" class rather than our equivalent
    # "beartype.cave.FunctionType" class to avoid circular import issues.
    return (
        # If this function is pure-Python, this function's code object.
        func.__code__ if isinstance(func, FunctionType) else
        # Else, "None".
        None
    )