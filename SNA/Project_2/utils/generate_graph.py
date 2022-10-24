import snap
import graphviz


class GenerateGraph:

    def __init__(self, nodes):
        self.nodes = nodes
        self.graph = snap.GenCircle(snap.TUNGraph, self.nodes, 1)

    def make_euler_path_without_circuit(self):
        """Edits a connected GenCircle graph in order to have an euler path."""
        NId_1: int = self.graph.GetRndNId()
        NId_2: int = self.graph.GetRndNId()
        print(f"Connecting {NId_1} to {NId_2}")
        self.graph.AddEdge(NId_1, NId_2)
        return self.graph

    def random_Circlegraph(self, plot: bool = False) -> snap.GenFull:
        """
        Generates a random graph using GenCircle. If plot=True is provided, a file will be saves with the plot
        visualised (Should be avoided in large graphs)
        """

        if plot:
            snap.DrawGViz(self.graph, snap.gvlDot, "gviz.png", "Graph")

        return self.graph
