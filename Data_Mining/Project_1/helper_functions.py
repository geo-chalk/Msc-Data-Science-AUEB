from itertools import combinations
from collections import defaultdict
import pandas as pd
import csv
from typing import Tuple, List, Dict, Set
from random import Random, randint
import numpy as np
import sys
from pprint import pprint
import pickle as pkl
import os
from pathlib import Path


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


def compute_jaccard_hash(data: pd.DataFrame, similar_users: List[set]) -> Dict[int, list]:
    """
    Compute exact jaccard scores given a df

    Args:
        data: imput data
        similar_users: List contraining the set of users with exact jarracd score > 0.5%

    """

    # create pairs (user1, user2)
    pairs = list(combinations(list(data.index), 2))
    usim = defaultdict(dict)

    doc_length = data.shape[1]
    sys.stdout.write("Started Evaluation...")
    for i, (user_1, user_2) in enumerate(pairs):

        s1: pd.Series = data.loc[user_1]
        s2: pd.Series = data.loc[user_2]

        common_movies = np.count_nonzero(s1 == s2)

        jacc: float = common_movies / doc_length

        if jacc >= 0.5 or {user_1, user_2} in similar_users:
            usim[user_1][user_2]: float = jacc

        if i % 10000 == 0 and i != 0:
            sys.stdout.flush()
            sys.stdout.write(f"\rEvaluated {i}/{len(pairs)} pairs")

    sys.stdout.flush()
    sys.stdout.write("\r")
    neighbors_u: dict = {user: sorted(usim[user].items(), key=lambda x: x[1], reverse=True) for user in usim}

    scores: dict = dict(sorted(neighbors_u.items(), key=lambda item: item[1][0][1], reverse=True))

    return scores


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

    Returns:
        hashing: a list of np.arrays with the permutations (hashing)
    """



    # initialize a, b generator
    generator = generate_a_b(R, iteration)
    hashing: List[np.ndarray] = []

    for _ in range(n):

        a, b = next(generator) # yield next a, b pair
        _hash: np.ndarray = (a * rows + b) % R
        hashing.append(_hash)

    return hashing


def find_optimal_R(rows: np.ndarray, number_of_movies: int) -> int:
    """
    Find the optimal value for R, which will not create conflicts

    Args:
        rows: the rows which is the index of each movie
        number_of_movies: total number of movies

    Returns:
        first prime number for which we do not have has collisions
    """
    for _prime in primes(100000):
        a, b = randint(0, _prime), randint(0, _prime)
        hashing = (a * rows + b) % _prime

        # break if number of unique rows is equal to the number of rows
        if len(np.unique(np.array(hashing))) >= number_of_movies:
            R: int = _prime
            return R


def generate_signatures(n: int, movies: pd.DataFrame, R: int, iteration: int) -> pd.DataFrame:
    """
    Generate the signature of each user based on the movie vector

    Args:
        n: number of minhash function to create the signature
        movies: pandas dataframe containing the movies each user has seen in an embedding format
        R: a large prime number
        iteration: number based on which a and b will be randomized (to avoid duplicates and allow reproduction

    Returns:
        signature: the signature of each user generated by the has functions

    """
    # Define movie index rows
    rows: np.ndarray = np.array(range(1, len(movies[1]) + 1))

    hash_functions: List[np.ndarray] = generate_hashing(n=n, rows=rows, R=R, iteration=iteration)
    min_hash = []

    # for n has functions
    for i in range(n):
        hash_func = hash_functions[i]

        # add the hash function number where movies have 1 else add 9999, Then find the minhash value
        s = movies.apply(lambda x: np.where(np.array(x) == 1,  hash_func, 9999).min())
        min_hash.append(s)

    signature = pd.DataFrame(np.array(min_hash).tolist()).T
    signature.index = np.arange(1, len(signature) + 1)

    return signature


def evaluate_jaccard(jaccard_scores: Dict[int, list],
                     similar_users: List[Set[int]],
                     n: int,
                     iteration: int,
                     writer: csv.writer = None) -> defaultdict:
    """
    Evaluate estimated jaccard scores against the actual jaccard scores & write the results to a csv file.

    Args:
        jaccard_scores: estimated jaccard scores
        similar_users: similar users (>=50%) based on actual scores
        n: The number of hash functions
        iteration: The current iteration (starting from 1)
        writer: csv.writer to write the results

    Returns:

    """

    evaluation = defaultdict(int)

    for user_1, sim_users in jaccard_scores.items():
        for (user_2, users_scores) in sim_users:
            if {user_1, user_2} in similar_users:
                if users_scores >= 0.5:
                    writer.writerow([n, iteration, user_1, user_2, users_scores, "True Positive"])
                    evaluation["True Positives"] += 1
                if users_scores < 0.5:
                    writer.writerow([n, iteration, user_1, user_2, users_scores, "False Negative"])
                    evaluation["False Negatives"] += 1
            else:
                writer.writerow([n, iteration, user_1, user_2, users_scores, "False Positive"])
                evaluation["False Positives"] += 1
    pprint(dict(evaluation))
    return evaluation


def load_file(path: str) -> pd.DataFrame:
    """Load a pickle file if it exists"""
    try:
        with open(path, 'rb') as f:
            signature = pkl.load(f)
            print(signature.shape)
    except FileNotFoundError:
        raise FileNotFoundError(f"Signature variable not loaded. Please run the notebook once again to load it, "
                                f"or place the '{path}' file under {os.getcwd()}.")


def print_similar_pairs(jaccard_scores: list) -> None:
    """Print the pair of users with similar Jaccard Scores (>=0.5)"""

    # output scores
    similar_users = []
    for user1, sim_users in jaccard_scores.items():
        for user_score in sim_users:
            similar_users.append({user1, user_score[0]})
            print(f"Pair: ({user1}, {user_score[0]}) - Jaccard Score: {user_score[1]*100:.2f}%")
    return similar_users


def load_file(path: str) -> pd.DataFrame:
    """Load a pickle file if it exists"""
    try:
        with open(path, 'rb') as f:
            _signature = pkl.load(f)
            return _signature
    except FileNotFoundError:
        raise FileNotFoundError(f"Signature variable not loaded. Please run the notebook once again to load it, "
                                f"or place the '{path}' file under {os.getcwd()}.")


def calculate_similar_users_LSH(r: int, iteration: int) -> List[set]:
    """
    Calculate similar users based on the LSH estimation

    Args:
        r: number of rows per band
        iteration: current iteration

    Returns:
        similar_users_band: distinct pair of candidate pairs

    """

    similar_users_band: list = []
    signature = load_file(path=Path("files") / f"signature_200_{iteration}.pkl")

    # split into r rows
    for i, start in enumerate(range(0, signature.shape[1], r)):

        chunk = signature.loc[:,start:(i+1)*r-1]

        # fetch duplicate rows and sort by columns. The indices will match in a step of 2
        candidates = chunk[chunk.duplicated(keep=False)].sort_values(by=[col for col in chunk.columns])

        # if we find similar rows, take the pairs per two
        if not candidates.empty:

            for i, k in zip(candidates.index[0::2], candidates.index[1::2]):
                if {i, k} not in similar_users_band:
                    similar_users_band.append({i, k})

    return similar_users_band
