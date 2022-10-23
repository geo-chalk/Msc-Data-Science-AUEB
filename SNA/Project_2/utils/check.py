from typing import Union
from snap import TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet, IsConnected
import snap


def odd_degree(graph: Union[TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet]) -> bool:
    """Check the odd degree vertices and return them (if any)."""

    _vertices: list = []
    for NI in graph.Nodes():
        if NI.GetDeg() % 2 != 0:
            _vertices.append(NI.GetId())
    return set(_vertices)


def has_odd_degree(graph: Union[TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet]) -> bool:
    """Check if there is at least one graph with odd degree"""

    _vertices: list = []
    for NI in graph.Nodes():
        if NI.GetDeg() % 2 != 0:
            print(f"Odd Degree found!!! Node: {NI.GetId()} Degree: {NI.GetDeg()}")
            return True
    return False