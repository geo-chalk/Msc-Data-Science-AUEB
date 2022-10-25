import snap
import pandas as pd
from .GOBALS import *
import time
import random
import multiprocessing


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


class AlgorithmComparison:

    def __init__(self, nodes: int, iter: int, df: pd.DataFrame):
        self.nodes = nodes
        self.iter = iter
        self.df = df
        self.graph = self.generate_graph()

    def generate_graph(self) -> snap.GenSmallWorld:
        """Function that generates a random graph using the Watts-Strogatz model."""
        Rnd = snap.TRnd(1, 0)
        return snap.GenSmallWorld(self.nodes, random.randint(5, 20), random.random(), Rnd)

    def highest_degrees(self) -> None:
        """Print the node with the highest degree along with it's degree"""
        highest_deg: list = [0, -1]
        for NI in self.graph.Nodes():
            if NI.GetDeg() > highest_deg[0]:
                highest_deg = [NI.GetDeg(), NI.GetId()]

        print(f"The Node with the highest degree is:")
        print(f"ID: {highest_deg[1]: >6} \nDegree: {highest_deg[0]: <10}")
        self.df.loc[self.iter, DEGREE_COLS] = [highest_deg[1], highest_deg[0]]

    def hub_and_auth(self) -> None:
        """Print the is and scores of the nodes with the highest Hubs and Authorities scores."""
        NIdHubH, NIdAuthH = self.graph.GetHits()

        highest_hub: list = [0, -1]
        for item in NIdHubH:
            if NIdHubH[item] > highest_hub[0]:
                highest_hub = [NIdHubH[item], item]

        print(f"The Node with the highest hub score is:")
        print(f"ID: {highest_hub[1]: >6} \nScore: {highest_hub[0]: >7.4f}")

        highest_auth: list = [0, -1]
        for item in NIdAuthH:
            if NIdAuthH[item] > highest_auth[0]:
                highest_auth = [NIdAuthH[item], item]
        print(f"The Node with the highest auth score is:")
        print(f"ID: {highest_auth[1]: >6} \nScore: {highest_auth[0]: >7.4f}")


    def run_community_detection(self, alg):
        print(f"\nRunning for algorithm: {alg}")
        start = time.time()
        modularity, CmtyV = getattr(self.graph, alg)()
        end = time.time()

        print(f"The modularity of the network is {modularity:.3f}.\nExecution time: {end-start:.3f}s\n")

    def print_results(self):
        self.highest_degrees()
        self.hub_and_auth()
        for alg in ("CommunityCNM", "CommunityGirvanNewman"):
            self.run_community_detection(alg)


