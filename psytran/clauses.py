# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

r"""
This module implements functions for querying clauses.
This includes whether :py:class:`Node`\s have OpenACC clauses
associated with them, as well as for applying such clauses, or a workaround
for the firstprivate issues on 3.1 version of PSyclone.
"""

from psyclone.psyir import nodes
from psyclone.psyir import symbols
from psytran.directives import (
    has_loop_directive,
    _check_directive,
)
from psytran.family import get_ancestors
from psytran.loop import _check_loop


__all__ = [
    "has_seq_clause",
    "has_gang_clause",
    "has_vector_clause",
    "has_collapse_clause",
    "first_priv_red_init",
]


def _prepare_loop_for_clause(loop, directive):
    """
    Prepare to apply a clause to a ``loop`` directive.

    :arg loop:       the Loop Node to prepare.
    :type loop:      :py:class:`Loop`
    :arg directive:  the directive to be applied
    :type directive: :py:class:`Directive`

    """
    _check_loop(loop)
    _check_directive(directive)


def has_seq_clause(loop):
    """
    Determine whether a loop has a ``seq`` clause.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``seq`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    return has_loop_directive(loop) and loop.parent.parent.sequential


def has_gang_clause(loop):
    """
    Determine whether a loop has a ``gang`` clause.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``gang`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    return has_loop_directive(loop) and loop.parent.parent.gang


def has_vector_clause(loop):
    """
    Determine whether a loop has a ``vector`` clause.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``vector`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    return has_loop_directive(loop) and loop.parent.parent.vector


def has_collapse_clause(loop):
    """
    Determine whether a loop lies within a collapsed loop nest.

    :arg loop: the Loop Node to query.
    :type loop: :py:class:`Loop`

    :returns: ``True`` if the Loop has a ``collapse`` clause, else ``False``.
    :rtype: :py:class:`bool`
    """
    _check_loop(loop)
    ancestors = get_ancestors(loop, inclusive=True)
    for i, current in enumerate(ancestors):
        if has_loop_directive(current):
            loop_dir = current.parent.parent
            collapse = loop_dir.collapse
            if collapse is None:
                continue
            return collapse > i
    return False


def first_priv_red_init(node_target, init_scalars):
    '''
    Add redundant initialisation before a Node, generally a Loop, where
    a OMP clause has firstprivate added by PSyclone.
    Software stack version of psyclone is adding firstprivates which fail
    with CCE.
    This is mostly fixed with PSyclone release 3.2, however that fix
    may still have unforeseen edge-cases.

    Parameters
    ----------
    Node : Target Node to reference from, adds redundant initialisation before.
    str list: List of str variable indexes to reference against.

    Returns
    ----------
    None : Note the tree has been modified
    '''
    # Ensure scalars that may be emitted as FIRSTPRIVATE have a value
    parent = node_target.parent
    insert_at = parent.children.index(node_target)
    for nm in init_scalars:  # e.g., ("jdir", "k")
        try:
            sym = node_target.scope.symbol_table.lookup(nm)
            # ensure character variables are initialised with CHARACTER_TYPE
            # rather than UnsupportedFortranType
            if isinstance(sym.datatype, symbols.UnsupportedFortranType):
                init = nodes.Assignment.create(
                    nodes.Reference(sym),
                    nodes.Literal("", symbols.CHARACTER_TYPE))
            else:
                init = nodes.Assignment.create(
                    nodes.Reference(sym),
                    nodes.Literal("0", sym.datatype))
            parent.children.insert(insert_at, init)
            insert_at += 1
        except KeyError:
            continue
