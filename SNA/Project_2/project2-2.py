import snap
import pandas as pd
from utils.helper_classes import AlgorithmComparison, CompareMetrics, ResultPlot
from pprint import pprint
import random
from utils.GOBALS import *

comm_values: list = [x for v in COMMUNITLY_COLS.values() for x in v]


def generate_dataframe() -> pd.DataFrame:
    """Generates an empty DataFrame with the required columns"""


    df_cols: list = BASIC_COLS + DEGREE_COLS + HUB_COLS + AUTH_COLS + comm_values
    df: pd.DataFrame = pd.DataFrame(columns=df_cols)
    return df

def print_dataframe(df: pd.DataFrame) -> None:
    """Prints there dataframe in a readable format"""
    print("-" * 130)
    print(df[BASIC_COLS + DEGREE_COLS].to_string(index=False))
    print("-" * 130)
    print(df[["Nodes"] + HUB_COLS + AUTH_COLS].to_string(index=False))
    print("-" * 130)
    print(df[["Nodes"] + comm_values].to_string(index=False))
    print("-" * 130, "\n"*10)


def main():

    # --- read df and max index --- #
    df = generate_dataframe()

    max_nodes: int = 0
    threshold_reached: bool = False
    for algorithm in ["CommunityCNM", "CommunityGirvanNewman"]:

        # --- For various nodes, compare and store algorithms --- #
        for i, nodes in enumerate(range(50, 1000000, 1000)):

            print(f"Running for {nodes} nodes")

            # --- if run exists skip it --- #
            if not df.loc[df.Nodes == nodes].empty:
                pass
            else:
                df.loc[i, BASIC_COLS] = [nodes, random.randint(5, 20), random.randint(0, 100) / 100]

            # --- run the community detection algorithm --- #
            threshold_reached = AlgorithmComparison(nodes=nodes, iter=i, df=df).print_results(_algorithms=[algorithm])
            if threshold_reached:
                break

            # --- save max nodes reached --- #
            if nodes > max_nodes:
                max_nodes = nodes
            print_dataframe(df)


            # --- Save results to csv --- #
            df.to_csv(f"project2-2_{algorithm}.csv", index=False)

    print(df.to_string(index=False))

    # --- find max calculated nodes and compute metrics --- #
    nodes = max_nodes
    print("\n"*5, f"Generating plots for {nodes} nodes")
    df_pagerank: pd.DataFrame = CompareMetrics(nodes=nodes).get_metrics()

    # sort by pagerank and print
    df_pagerank = df_pagerank.sort_values("PageRank", ascending=False).head(30)
    print(df_pagerank)

    ResultPlot(df_pagerank).generate_plots()


if __name__ == '__main__':
    main()
