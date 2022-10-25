import snap
import pandas as pd
from utils.helper_classes import AlgorithmComparison
from pprint import pprint
import random
from utils.GOBALS import *


def generate_dataframe() -> pd.DataFrame:
    """Generates an empty DataFrame with the required columns"""

    df_cols: list = BASIC_COLS + DEGREE_COLS + HUB_COLS + AUTH_COLS
    return pd.DataFrame(columns=df_cols)


def main():
    df = generate_dataframe()
    print(df.to_string(index=False))

    # --- For various nodes, compare and store algorithms --- #
    for i, nodes in enumerate([50, 100, 200, 300, 400]):
        df.loc[i, BASIC_COLS] = [nodes, random.randint(5, 20), random.randint(0, 100)/100]
        print(df.to_string(index=False))
        AlgorithmComparison(nodes=nodes, iter=i, df=df).print_results()


if __name__ == '__main__':
    main()
