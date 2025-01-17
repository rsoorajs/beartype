#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **path removers** (i.e., low-level callables permanently removing
on-disk files and directories in various reasonably safe and portable ways).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype.roar._roarexc import _BeartypeUtilPathException
from beartype._data.hint.datahinttyping import (
    PathnameLike,
    PathnameLikeTuple,
)
from importlib.machinery import BYTECODE_SUFFIXES
from pathlib import Path

# ....................{ REMOVERS                           }....................
#FIXME: Unit test us up, please.
def remove_package_bytecode_files(package_dirname: PathnameLike) -> None:
    '''
    Permanently, silently, and recursively remove all **bytecode files** (i.e.,
    pure-Python bytecode compiled to platform-dependent temporary files residing
    in temporary ``__pycache__/`` subdirectories) of both the passed package and
    all subpackages of that package regardless of nesting depth.

    Usage
    ----------
    This function is typically intended for usage in our test suite. Unit tests
    exercising :mod:`beartype` functionality that dynamically modifies the
    contents of bytecode files guarantee idempotency (i.e., reproducibility) by
    calling this function *before* exercising that functionality. Examples
    include :mod:`beartype.claw` import hooks that dynamically transform the
    abstract syntax trees (ASTs) of sample modules embedded in our test suite
    *before* permanently serializing (i.e., saving, writing) those changes back
    to disk within those bytecode files. Preventing desynchronization between
    the frequently changing implementations of those import hooks and those
    bytecode files requires calling this function beforehand.

    Caveats
    ----------
    **This function is subject to subtle race conditions if multiple threads
    and/or processes concurrently attempt to mutate this package on the local
    filesystem.** Since *all* filesystem-centric logic suffers similar issues,
    we leave this issue as an exercise for the caller.

    Parameters
    ----------
    package_dirname : PathnameLike
        Absolute dirname of the package to remove all previously compiled
        bytecode files from.
    '''
    assert isinstance(package_dirname, PathnameLikeTuple), (
        f'{repr(package_dirname)} neither string nor "Path" object.')

    # Avoid circular import dependencies.
    from beartype._util.path.utilpathtest import die_unless_dir

    # High-level "Path" object encapsulating this dirname.
    package_dir = Path(package_dirname)

    # If this directory does *NOT* exist, raise an exception.
    die_unless_dir(package_dir)
    # Else, this directory exists.

    # For the "."-prefixed filetype of each type of platform-dependent bytecode
    # file generated by the current platform...
    #
    # Note that Python-specific glob syntax does *not* support disjunction
    # (i.e., alternation). In particular, POSIX-compliant glob disjunction
    # syntax "{match1,...,matchN}" is unsupported. If supported, that syntax
    # would enable this inefficient O(n) iteration to be trivially optimized
    # into a single O(1) call to the remove_paths_globbed() function.
    for BYTECODE_SUFFIX in BYTECODE_SUFFIXES:
        # Permanently and silently remove *ALL* bytecode files previously
        # compiled by Python into this "__pycache__/" subdirectory.
        remove_paths_globbed(
            dirname=package_dir,
            # Note that this filetype is already prefixed by ".". *sigh*
            glob=f'**/__pycache__/*{BYTECODE_SUFFIX}',
        )


#FIXME: Unit test us up, please.
def remove_paths_globbed(dirname: PathnameLike, glob: str) -> None:
    '''
    Permanently, silently, and possibly recursively remove *all* target files
    and empty directories from the source directory with the passed dirname
    matching the passed Python-specific glob expression.

    Note that Python-specific glob syntax is exactly that supported by the
    standard :mod:`fnmatch` module *plus* the recursive glob syntax ``"**/"``.
    Specifically, Python-specific glob syntax supports *only* the following
    small subset of POSIX-compliant glob syntax:

    * ``"*"`` matches everything.
    * ``"?"`` matches any single character.
    * ``"[seq]"`` matches any character in the substring ``"seq"``.
    * ``"[!seq]"`` matches any character not in the substring ``"seq"``.
    * ``"**/"`` matches *all* subdirectories recursively regardless of depth
      (e.g., ``"**/*.jpg"``, recursively removing all JPEG-formatted images from
      both this directory and all subdirectories of this directory).

    Caveats
    ----------
    **This function silently ignores all non-empty directories matched by this
    glob expression.** Consider an alternate approach leveraging recursive
    directory tree traversal if requiring non-empty directory removal.

    **This function is subject to subtle race conditions if multiple threads
    and/or processes concurrently attempt to mutate this source directory.**
    Since *all* filesystem-centric logic suffers similar issues, we leave this
    issue as an exercise for the caller.

    **This function is currently inefficiently implemented in a single-threaded
    manner for simplicity.** This approach is appropriate when removing a small
    number of files but inappropriate when removing a large number of files. In
    the latter case, consider an alternate approach leveraging either
    multithreading or multiprocessing. See also this `popular article`_.

    .. _popular article:
        https://superfastpython.com/multithreaded-file-deletion

    Parameters
    ----------
    dirname : PathnameLike
        Dirname of the directory to remove *all* files and empty directories
        matching this glob from, specified as a **pathname-like** (i.e., either
        a low-level string possibly signifying a pathname *or* a high-level
        :class:`Path` instance definitely encapsulating a pathname).
    glob : str
        Python-specific glob expression matching *all* files and empty
        directories to be removed from this directory (e.g., ``"*.jpg"``).

    Raises
    ----------
    _BeartypeUtilPathException
        If either:

        * This directory does *not* exist.
        * This directory exists but is *not* actually a directory.

    See Also
    ----------
    https://stackoverflow.com/a/38189275/2809027
        StackOverflow answer strongly inspiring this implementation.
    '''
    assert isinstance(dirname, PathnameLikeTuple), (
        f'{repr(dirname)} neither string nor "Path" object.')
    assert isinstance(glob, str), f'{repr(glob)} not string.'

    # Avoid circular import dependencies.
    from beartype._util.path.utilpathtest import die_unless_dir

    # High-level "Path" object encapsulating this dirname.
    dirname_path = Path(dirname)

    # If this directory does *NOT* exist, raise an exception.
    die_unless_dir(dirname_path)
    # Else, this directory exists.

    # For each matching pathname globbed from this dirname as a "Path" object...
    for pathname_globbed in dirname_path.glob(glob):
        # print(f'Removing globbed path "{pathname_globbed}"...')

        # If this pathname refers to a file...
        if pathname_globbed.is_file():
            #FIXME: Pass "missing_ok=True" *AFTER* dropping Python 3.7, as doing
            #so will improve the robustness of this logic against race
            #conditions.

            # Silently remove this file if feasible *OR* raise an exception.
            pathname_globbed.unlink()
        # Else, this pathname does *NOT* refer to a file.
        #
        # If this pathname refers to a (hopefully empty) subdirectory...
        elif pathname_globbed.is_dir():
            # Silently remove this empty subdirectory if feasible *OR* raise an
            # exception.
            pathname_globbed.rmdir()
        # Else, this pathname refers to neither a file *NOR* subdirectory. In
        # this case, silently ignore this pathname.
