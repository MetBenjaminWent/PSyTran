from fparser.common.readfortran import FortranStringReader
from psyclone.psyGen import PSyFactory


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
