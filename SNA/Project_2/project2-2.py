import snap
import pandas as pd
from utils.helper_classes import AlgorithmComparison
from pprint import pprint
import random
from utils.GOBALS import *

comm_values: list = [x for v in COMMUNITLY_COLS.values() for x in v]

def generate_dataframe() -> pd.DataFrame:
    """Generates an empty DataFrame with the required columns"""

    df_cols: list = BASIC_COLS + DEGREE_COLS + HUB_COLS + AUTH_COLS + comm_values
    return pd.DataFrame(columns=df_cols)

def print_dataframe(df: pd.DataFrame) -> None:
    """Prints there dataframe in a readable format"""
    print("-" * 130)
    print(df[["Nodes"] + BASIC_COLS + DEGREE_COLS].to_string(index=False))
    print("-" * 130)
    print(df[["Nodes"] + HUB_COLS + AUTH_COLS].to_string(index=False))
    print("-" * 130)
    print(df[["Nodes"] + comm_values].to_string(index=False))
    print("-" * 130, "\n"*10)


def main():
    df = generate_dataframe()

    threshold_reached: bool = False
    # --- For various nodes, compare and store algorithms --- #
    for i, nodes in enumerate(range(50, 500, 20)):

        df.loc[i, BASIC_COLS] = [nodes, random.randint(5, 20), random.randint(0, 100)/100]
        threshold_reached = AlgorithmComparison(nodes=nodes, iter=i, df=df).print_results()
        if threshold_reached:
            break
        print_dataframe(df)

    print(df.to_string(index=False))
    # --- Save results to csv --- #
    df.to_csv("project2-2.csv")

if __name__ == '__main__':
    main()
