from typing import Union
from snap import TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet, IsConnected
import snap
import unittest
from utils import check




def has_euler_path(
        graph: Union[TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet]
        ) -> tuple:
    """
    Check if a given graph has an euler path.
    Graph should be connected and the number of odd degree nodes should be 2.

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

    # --- Check number of odd vertices --- #
    vertices = check.odd_degree(graph)
    if len(vertices) == 2:
        return False, vertices
    else:
        return True, vertices





def has_euler_circuit(
        graph: Union[TUNGraph, TUNGraph, TUNGraphNodeI, TUNGraphEdgeI, TNGraph, TNGraphNodeI, TNGraphEdgeI, TNEANet]
        ) -> bool:
    """
    Check if a given graph has an euler circuit.
    Args:
        graph: any SNAP graph class. See SNAP documentation for the full list.

    Returns:
        bool
    """
    ## FILL HERE

    # --- Check if the graph is connected -- #
    if not graph.IsConnected():
        return False
    return False

class TestEulerMethods(unittest.TestCase):

    def test_has_euler_path_but_not_circuit(self):
        # FILL HERE
        result, vertices = has_euler_path(graph)
        self.assertTrue(result)
        self.assertEqual(len(vertices), 2)

    def test_does_not_have_euler_path(self):
        # FILL HERE
        result, vertices = has_euler_path(graph)
        self.assertFalse(result)
        self.assertEqual(len(vertices), 0)

    def test_has_euler_circuit(self):
        # FILL HERE
        result = has_euler_circuit(graph)
        self.assertTrue(result)
        self.assertTrue(graph.GetNodes()>=1000)

    def test_does_not_have_euler_circuit(self):
        # FILL HERE
        result = has_euler_circuit(graph)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
