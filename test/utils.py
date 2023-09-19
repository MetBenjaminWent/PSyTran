from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory
from psyacc import *
import code_snippets as cs
import ukca_code as ukca

has_clause = {
    "sequential": has_seq_clause,
    "gang": has_gang_clause,
    "vector": has_vector_clause,
}

apply_clause = {
    "sequential": apply_loop_seq,
    "gang": apply_loop_gang,
    "vector": apply_loop_vector,
}


def get_schedule(parser, code_string):
    """
    Given a snippet of test code written as a string, get the schedule of the
    (first) invoke it contains.

    :arg parser: the parser type to be used
    :arg code_string: the code to be parsed, as a string
    """
    code = parser(FortranStringReader(code_string))
    psy = PSyFactory("nemo", distributed_memory=False).create(code)
    return psy.invokes.invoke_list[0].schedule


def simple_loop_code(depth):
    """
    Generate a code string containing a perfectly nested loop with a single
    assignment at the deepest level.

    :arg depth: number of loops in the nest
    """
    if depth == 1:
        return cs.loop_with_1_assignment
    elif depth == 2:
        return cs.double_loop_with_1_assignment
    elif depth == 3:
        return cs.triple_loop_with_1_assignment
    elif depth == 4:
        return cs.quadruple_loop_with_1_assignment
    else:
        raise NotImplementedError
