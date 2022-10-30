from __future__ import print_function
import snap
import pandas as pd
from .GOBALS import *
import time
import random
from functools import wraps

import sys
import threading
from time import sleep
try:
    import thread
except ImportError:
    import _thread as thread


def quit_function(fn_name):
    # print to stderr, unbuffered in Python 2.
    print('{0} took too long'.format(fn_name), file=sys.stderr)
    sys.stderr.flush() # Python 3 stderr is likely buffered.
    thread.interrupt_main() # raises KeyboardInterrupt


def exit_after(s):
    '''
    use as decorator to exit process if
    function takes longer than s seconds
    '''
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer


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
        return snap.GenSmallWorld(self.nodes, self.df.at[self.iter, "NodeOutDeg"],
                                  self.df.at[self.iter, "RewireProb"],
                                  Rnd)


    def highest_degrees(self) -> None:
        """Print the node with the highest degree along with it's degree"""
        highest_deg: list = [0, -1]
        for NI in self.graph.Nodes():
            if NI.GetDeg() > highest_deg[0]:
                highest_deg = [NI.GetDeg(), NI.GetId()]

        # print(f"The Node with the highest degree is:")
        # print(f"ID: {highest_deg[1]: >6} \nDegree: {highest_deg[0]: <10}")
        self.df.loc[self.iter, DEGREE_COLS] = [highest_deg[1], highest_deg[0]]

    def hub_and_auth(self) -> None:
        """Print the is and scores of the nodes with the highest Hubs and Authorities scores."""
        NIdHubH, NIdAuthH = self.graph.GetHits()

        # --- Buhs Score --- #
        highest_hub: list = [0, -1]
        for item in NIdHubH:
            if NIdHubH[item] > highest_hub[0]:
                highest_hub = [NIdHubH[item], item]
        # update df and print
        self.df.loc[self.iter, HUB_COLS] = [highest_hub[1], highest_hub[0]]
        # print(f"The Node with the highest hub score is:")
        # print(f"ID: {highest_hub[1]: >6} \nScore: {highest_hub[0]: >7.4f}")

        # --- Authorities Score --- #
        highest_auth: list = [0, -1]
        for item in NIdAuthH:
            if NIdAuthH[item] > highest_auth[0]:
                highest_auth = [NIdAuthH[item], item]
        # update df and print
        self.df.loc[self.iter, AUTH_COLS] = [highest_auth[1], highest_auth[0]]
        # print(f"The Node with the highest auth score is:")
        # print(f"ID: {highest_auth[1]: >6} \nScore: {highest_auth[0]: >7.4f}")

    @exit_after(60*10)
    def run_community_detection(self, _alg):
        print(f"\nRunning for algorithm: {_alg}")
        start = time.time()
        modularity, CmtyV = getattr(self.graph, _alg)()
        end = time.time()

        self.df.loc[self.iter, COMMUNITLY_COLS.get(_alg)] = [end-start, modularity]
        print(f"The modularity of the network is {modularity:.3f}.\nExecution time: {end-start:.3f}s\n")

    def print_results(self):
        self.highest_degrees()
        self.hub_and_auth()
        for alg in ("CommunityCNM", "CommunityGirvanNewman"):
            try:
                self.run_community_detection(alg)
            except KeyboardInterrupt:
                print(f"Timeout Reached. Stopping algorithm.")
                return True
            except MemoryError:
                print(f"Memory Error. Stopping algorithm.")
                return True
        return False



