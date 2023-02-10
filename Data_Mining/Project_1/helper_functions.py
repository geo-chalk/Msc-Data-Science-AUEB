from itertools import combinations
from collections import defaultdict
import pandas as pd
from typing import Tuple, List, Dict
from random import shuffle, Random
import numpy as np


def compute_jaccard(data: pd.Series, threshold: float = 0.5) -> Dict[int, dict]:
    """
    Compute exact jaccard scores given a df

    Args:
        data: imput data
        threshold: value which determined the threshold according to which users will be considered similar

    """

    # create pairs (user1, user2)
    pairs = list(combinations(list(data.keys()), 2))
    usim = defaultdict(dict)

    for user_1, user_2 in pairs:
        s1: set = data[user_1]
        s2: set = data[user_2]


        union = s1.union(s2)
        inter = s1.intersection(s2)

        jacc: float = len(inter)/len(union)

        if jacc >= 0.5:
            usim[user_1][user_2]: float = jacc

    neighbors_u: dict = {user: sorted(usim[user].items(), key=lambda x: x[1], reverse=True) for user in usim}

    scores: Dict[int, dict] = dict(sorted(neighbors_u.items(), key=lambda item: item[1][0][1], reverse=True))
    return scores


def compute_jaccard_hash(data: pd.Series) -> Tuple[dict, defaultdict]:
    """
    Compute exact jaccard scores given a df

    Args:
        data: imput data

    """

    # create pairs (user1, user2)
    pairs = list(combinations(list(data.index), 2))
    usim = defaultdict(dict)

    doc_length = data.shape[1]
    for user_1, user_2 in pairs:
        s1: pd.Series = data.loc[user_1]
        s2: pd.Series = data.loc[user_2]

        common_movies = np.count_nonzero(s1 == s2)

        jacc: float = common_movies/doc_length

        usim[user_1][user_2]: float = jacc

    neighbors_u: dict = {user: sorted(usim[user].items(), key=lambda x: x[1], reverse=True) for user in usim}

    scores: dict = dict(sorted(neighbors_u.items(), key=lambda item: item[1][0][1], reverse=True))
    return scores, usim


def primes(n: int) -> list:
    """ Returns  a list of primes < n """
    sieve = [True] * n
    for i in range(3, int(n**0.5)+1, 2):
        if sieve[i]:
            sieve[i*i::2*i]=[False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3, n, 2) if sieve[i]]


def generate_a_b(R: int, random_seed: int) -> Tuple[int, int]:
    """
    Generates the required values for a and b making sure that they are different
    Args:
        R: a prime number
        random_seed: random_seed for reproductability purposes
    """

    # initialize lists
    a_list: list = list(range(0, R))
    Random(random_seed).shuffle(a_list)
    b_list: list = list(range(0, R))
    Random(random_seed).shuffle(b_list)

    # iterate
    while True:
        a: int = a_list.pop()
        b: int = b_list.pop()
        while b == a:
            b: int = b_list.pop()

        yield a, b


def generate_hashing(n: int, rows: np.ndarray, R: int, iteration: int = 42) -> List[np.ndarray]:
    """
    Generates n hash functions given the rows of each user's movie.
    Hash function is of the form (ax + b) % R, where a and b are random
    numbers between 0 and R, and are different for each hash function

    Args:
        n: number of hashing functions
        rows: number of rows, equal to the user's movie signature
        R: the modifier of the hashing function
        iteration: the current iteration, in case of multiple runs
    """



    # initialize a, b generator
    generator = generate_a_b(R, iteration)
    hashing: List[np.ndarray] = []

    for _ in range(n):

        a, b = next(generator) # yield next a, b pair
        _hash:np.ndarray = (a * rows + b) % R
        hashing.append(_hash)

    return hashing
