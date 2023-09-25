from psyclone.psyir import nodes
from psyclone.psyir import transformations as trans
from psyclone.domain.nemo import transformations as nemo_trans
from psyclone.psyir import symbols
from psyclone.transformations import TransformationError

__all__ = ["convert_array_notation", "convert_range_loops"]


def convert_array_notation(schedule):
    """
    Convert implicit array range assignments into explicit ones.

    Wrapper for the :meth:`apply` method of :class:`Reference2ArrayRangeTrans`.
    """
    for reference in schedule.walk(nodes.Reference, stop_type=nodes.Reference):
        if isinstance(reference.symbol, symbols.DataSymbol):
            try:
                trans.Reference2ArrayRangeTrans().apply(reference)
            except TransformationError:
                pass


def convert_range_loops(schedule):
    """
    Convert explicit array range assignments into loops.

    Wrapper for the :meth:`apply` method of :class:`NemoAllArrayRange2LoopTrans`.
    """
    for assign in schedule.walk(nodes.Assignment):
        try:
            nemo_trans.NemoAllArrayTrans2LoopTrans().apply(assign)
        except TransformationError:
            pass
