from __future__ import print_function
import snap
import pandas as pd
import matplotlib.pyplot as plt
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
        return snap.GenSmallWorld(self.nodes, int(self.df.at[self.iter, "NodeOutDeg"]),
                                  self.df.at[self.iter, "RewireProb"],
                                  Rnd)

    def highest_degrees(self) -> None:
        """Print the node with the highest degree along with it's degree"""
        highest_deg: list = [0, -1]
        for NI in self.graph.Nodes():
            if NI.GetDeg() > highest_deg[0]:
                highest_deg = [NI.GetDeg(), NI.GetId()]


        self.df.loc[self.iter, DEGREE_COLS] = [highest_deg[1], highest_deg[0]]

    def hub_and_auth(self) -> None:
        """Print the is and scores of the nodes with the highest Hubs and Authorities scores."""
        NIdHubH, NIdAuthH = self.graph.GetHits()

        # --- Hubs Score --- #
        highest_hub: list = [0, -1]
        for item in NIdHubH:
            if NIdHubH[item] > highest_hub[0]:
                highest_hub = [NIdHubH[item], item]
        # update df and print
        self.df.loc[self.iter, HUB_COLS] = [highest_hub[1], highest_hub[0]]

        # --- Authorities Score --- #
        highest_auth: list = [0, -1]
        for item in NIdAuthH:
            if NIdAuthH[item] > highest_auth[0]:
                highest_auth = [NIdAuthH[item], item]
        # update df and print
        self.df.loc[self.iter, AUTH_COLS] = [highest_auth[1], highest_auth[0]]


    @exit_after(60*10)
    def run_community_detection(self, _alg):
        print(f"\nRunning for algorithm: {_alg}")
        start = time.time()
        modularity, CmtyV = getattr(self.graph, _alg)()
        end = time.time()

        self.df.loc[self.iter, COMMUNITLY_COLS.get(_alg)] = [end-start, modularity]
        print(f"The modularity of the network is {modularity:.3f}.\nExecution time: {end-start:.3f}s\n")

    def print_results(self, _algorithms: list = ["CommunityCNM", "CommunityGirvanNewman"]):
        self.highest_degrees()
        self.hub_and_auth()
        for alg in _algorithms:
            try:
                self.run_community_detection(alg)
            except KeyboardInterrupt:
                print(f"Timeout Reached. Stopping algorithm.")
                return True
            except MemoryError:
                print(f"Memory Error. Stopping algorithm.")
                return True
        return False


class CompareMetrics:
    def __init__(self, nodes: int):
        self.nodes = nodes
        self.graph = self.generate_graph()

    def generate_graph(self) -> snap.GenSmallWorld:
        """Function that generates a random graph using the Watts-Strogatz model."""

        Rnd = snap.TRnd(1, 0)
        return snap.GenSmallWorld(self.nodes, random.randint(5, 20),
                                  random.randint(0, 100) / 100,
                                  Rnd)

    @staticmethod
    def snap_to_array(TIntFltH: snap.TIntFltH, metric: str) -> dict:
        """
        Returns a dictionary having the metric (eg PageRank) as key and value the calulcated score for each node.

        Args:
            TIntFltH: snap.TIntFltH object
            metric: str describing the calculated score

        Returns:
            dict of the format {str: list}
        """
        _val: list = [TIntFltH[item] for item in TIntFltH]

        return {metric: _val}

    def get_PageRank(self) -> dict:
        """Calculates and returns the PageRank for all nodes"""
        PRankH = self.graph.GetPageRank()

        return self.snap_to_array(PRankH, "PageRank")

    def get_betweeness_centr(self)-> dict:
        """Calculates and returns the Betweenness Centrality for all nodes"""
        Nodes, Edges = self.graph.GetBetweennessCentr(1.0)
        return self.snap_to_array(Nodes, "BetweennessCentr")

    def get_closeness_centr(self) -> dict:
        """Calculates and returns the closeness Centrality for all nodes"""
        CloseCentr = [self.graph.GetClosenessCentr(NI.GetId()) for NI in self.graph.Nodes()]
        return {"ClosenessCentr": CloseCentr}

    def get_hubs_auth(self) -> dict:
        """Calculates and returns the Hubs and Authority scores for all nodes"""
        NIdHubH, NIdAuthH = self.graph.GetHits()

        res = {**self.snap_to_array(NIdHubH, "HubScore"), **self.snap_to_array(NIdAuthH, "AuthScore")}
        return res

    def get_metrics(self) -> pd.DataFrame:
        """Generates the following metrics: Betweenness, Closeness, PageRank, Authority and Hub Score"""
        metrics: dict = {}
        metrics.update(self.get_PageRank())
        metrics.update(self.get_betweeness_centr())
        metrics.update(self.get_closeness_centr())
        metrics.update(self.get_hubs_auth())
        return pd.DataFrame(metrics)

class ResultPlot:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def generate_plots(self):
        """Calls required methods to generate plots"""
        self.betweenness_closeness()
        self.auth_hub()

    def betweenness_closeness(self):
        """Plots Betweenness, Closeness and PageRank"""

        # Keep only columns needed
        _df = self.df[["PageRank", "ClosenessCentr", "BetweennessCentr"]]
        x_tick_labels = _df.index.values

        # define axes and titles
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel("Node ID")
        ax1.set_ylabel("PageRank")

        ax2 = ax1.twinx()
        ax2.set_ylabel("ClosenessCentr")

        ax3 = ax1.twinx()
        ax3.set_ylabel("BetweennessCentr")


        # plot the axes
        _df.reset_index(inplace=True)
        p1 = _df.PageRank.plot(kind="bar", color="tab:gray", ax=ax1, alpha=0.5, label="PageRank")
        p2 = _df.ClosenessCentr.plot(kind="line", color="tab:orange", ax=ax3, label="ClosenessCentr")
        p3 = _df.BetweennessCentr.plot(kind="line", color="tab:blue", ax=ax2, label="BetweennessCentr")

        ax1.set_xticklabels(x_tick_labels)
        ax3.spines['right'].set_position(('outward', 50))

        # coloring
        ax1.yaxis.label.set_color("tab:gray")
        ax1.tick_params(axis='y', colors='tab:gray')
        ax2.yaxis.label.set_color("tab:orange")
        ax2.tick_params(axis='y', colors='tab:orange')
        ax3.yaxis.label.set_color("tab:blue")
        ax3.tick_params(axis='y', colors='tab:blue')

        fig.tight_layout()
        fig.savefig("plots/betweenness_closeness_pagerank.png")
        plt.show()

    def auth_hub(self):
        """Plots Hub and Authority scores and PageRank"""

        # Keep only columns needed
        _df = self.df[["PageRank", "HubScore", "AuthScore"]]
        x_tick_labels = _df.index.values

        # define axes and titles
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel("Node ID")
        ax1.set_ylabel("PageRank")

        ax2 = ax1.twinx()
        ax2.set_ylabel("HubScore")

        ax3 = ax1.twinx()
        ax3.set_ylabel("AuthScore")


        # plot the axes
        _df.reset_index(inplace=True)
        p1 = _df.PageRank.plot(kind="bar", color="tab:gray", ax=ax1, alpha=0.5, label="PageRank")
        p2 = _df.HubScore.plot(kind="line", color="tab:orange", ax=ax3, label="HubScore")
        p3 = _df.AuthScore.plot(kind="line", color="tab:blue", ax=ax2, label="AuthScore")

        ax1.set_xticklabels(x_tick_labels)
        ax3.spines['right'].set_position(('outward', 50))

        # coloring
        ax1.yaxis.label.set_color("tab:gray")
        ax1.tick_params(axis='y', colors='tab:gray')
        ax2.yaxis.label.set_color("tab:orange")
        ax2.tick_params(axis='y', colors='tab:orange')
        ax3.yaxis.label.set_color("tab:blue")
        ax3.tick_params(axis='y', colors='tab:blue')

        fig.tight_layout()
        fig.savefig("plots/auth_hub_pagerank.png")
        plt.show()