from typing import Union
from snap import TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet, \
    IsConnected

import unittest
from utils import check
from utils.helper_classes import GenerateGraph


def has_euler_path(
        graph: Union[TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet]
) -> tuple:
    """
    Check if a given graph has an euler path.
    If a graph has an Euler path, then it must have exactly two vertices with odd degree,

    Args:
        graph: any SNAP graph class. See SNAP documentation for the full list.

    Returns:
        tuple:
            bool at index[0]
            set() at index[1]. The set contains the node id of the off_degree vertices if the graph has an euler path
    """
    vertices = set()
    ## FILL HERE

    # --- Check if the graph is connected -- #
    if not graph.IsConnected():
        return False, vertices

    # --- Check the number of odd vertices --- #
    vertices = check.odd_degree(graph)

    if len(vertices) == 2:
        return True, vertices
    else:
        return False, vertices


def has_euler_circuit(
        graph: Union[TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet]
) -> bool:
    """
    Check if a given graph has an euler circuit.
    If a graph has an Euler circuit, then all of its vertices must be of even degree.

    Args:
        graph: any SNAP graph class. See SNAP documentation for the full list.

    Returns:
        bool
    """
    ## FILL HERE

    # --- Check if the graph is connected -- #
    if not graph.IsConnected():
        return False

    # --- Check if there is at least an odd node --- #
    if check.has_odd_degree(graph):
        return False
    else:
        return True


class TestEulerMethods(unittest.TestCase):
    NODES = 1000

    def test_has_euler_path_but_not_circuit(self):
        # FILL HERE
        euler_graph = GenerateGraph(nodes=self.NODES).make_euler_path_without_circuit()
        result, vertices = has_euler_path(euler_graph)
        self.assertTrue(result)
        self.assertEqual(2, len(vertices))

    def test_does_not_have_euler_path(self):
        # FILL HERE
        euler_graph = GenerateGraph(nodes=self.NODES).random_Circlegraph()
        result, vertices = has_euler_path(euler_graph)
        self.assertFalse(result)
        self.assertEqual(len(vertices), 0)

    def test_has_euler_circuit(self):
        # FILL HERE
        euler_graph = GenerateGraph(nodes=self.NODES).random_Circlegraph()
        result = has_euler_circuit(euler_graph)
        self.assertTrue(result)
        self.assertTrue(euler_graph.GetNodes() >= 1000)

    def test_does_not_have_euler_circuit(self):
        # FILL HERE
        euler_graph = GenerateGraph(nodes=self.NODES).make_euler_path_without_circuit()
        result = has_euler_circuit(euler_graph)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
