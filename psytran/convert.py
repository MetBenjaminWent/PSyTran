# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

"""
This module provides functions for converting aspects of the tree including
symbols. This includes the array notation used in a
:py:class:`Schedule`, and a method for converting an n_threads reference
into a library call.
"""

from psyclone.psyir import nodes
from psyclone.psyir import transformations as trans
from psyclone.psyir import symbols
from psyclone.transformations import TransformationError
from psytran.family import has_ancestor

__all__ = ["convert_array_notation"]


def convert_array_notation(schedule):
    """
    Convert implicit array range assignments into explicit ones.

    Wrapper for the :meth:`apply` method of :class:`Reference2ArrayRangeTrans`.
    If this fails due to a :class:`TransformationError` then the conversion is
    skipped.

    :arg schedule: the Schedule to transform.
    :type schedule: :py:class:`Schedule`
    """
    for reference in schedule.walk(nodes.Reference, stop_type=nodes.Reference):
        if has_ancestor(reference, nodes.Call):
            continue
        if isinstance(reference.symbol, symbols.DataSymbol):
            try:
                trans.Reference2ArrayRangeTrans().apply(reference)
            except TransformationError:  # pragma: no cover
                pass


def replace_n_threads(psyir, n_threads_var_name):
    '''
    If a scheme would use omp_get_max_threads() to determine
    how work is divided, it will often be done so through
    an omp clause. PSyclone will remove this.
    We will therefore need to be able to add it to the source.
    With a given variable name for n_threads know by the developer
    in the source, replace its initialisation (often to 1) with
    omp_get_max_threads().

    Parameters
    ----------
    psyir object : Uses whole psyir representation
    n_threads_var_name str : The name of the variable in the
                             Scheme. Set relative to the scheme.

    Returns
    ----------
    None : Note the tree has been modified
    '''

    imported_lib = False
    # Walk the schedules
    for shed in psyir.walk(nodes.Schedule):
        # Walk the Assignments
        for assign in shed.walk(nodes.Assignment):
            # If the assignment has a lhs and is a reference...
            if isinstance(assign.lhs, nodes.Reference):
                # and that lhs name is n_threads_var_name
                if assign.lhs.name == n_threads_var_name:
                    # Do this once, but only if needed
                    if imported_lib is False:
                        # Get the symbol table of the current schedule
                        symtab = shed.symbol_table
                        # Set up the omp_library symbol
                        omp_lib = symtab.find_or_create(
                            "omp_lib",
                            symbol_type=symbols.ContainerSymbol)
                        # Set up the omp_get_max_threads symbol
                        omp_get_max_threads = symtab.find_or_create(
                            "omp_get_max_threads",
                            symbol_type=symbols.RoutineSymbol,
                            # Import the reference
                            interface=symbols.ImportInterface(omp_lib))
                        imported_lib = True
                    # Replace the rhs of the reference with the
                    # omp_get_max_threads symbol
                    assign.rhs.replace_with(
                        # pylint: disable=possibly-used-before-assignment
                        nodes.Call.create(omp_get_max_threads))
