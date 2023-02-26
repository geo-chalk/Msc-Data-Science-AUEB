import pandas as pd
from itertools import combinations
from collections import defaultdict

import sys


def progressbar(it, prefix="", size=60, out=sys.stdout, print_every=1000): # Python3.6+
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)


def discretize_rating(rating: float):
    """
    Converts a given float rating to a string value
    """
    polarity = 'A'  # average

    if rating < 2.5:
        polarity = 'N'  # negative
    elif rating > 3.5:
        polarity = 'P'  # positive

    return polarity


def load_ratings(ratings_df : pd.DataFrame,
                 focus : list # used to pick beer or user-based
                 ):

    """
    Loads all the ratings submitted by each user or all ratings submitted for a beer

    Returns:
        a dictionary that maps each user to a second dict that maps movies to discretized ratings

        OR

        a dictionary that maps each beer to a second dict that maps raters to discretized ratings

    """

    distinct_ids = set(ratings_df[focus[0]]) # get all distinct users

    ratings: set = {} # store ratings per entity

    for id_ in progressbar(distinct_ids, "Loading: ", 60): # for each user

        # get the info for every rating submitted for this user or for this beer
        my_ratings = ratings_df[ratings_df[focus[0]] == id_][[focus[1], 'review_overall']]

        # discretize the ratings and attach them to the user or to the beer
        ratings[id_] = dict(zip(my_ratings[focus[1]], my_ratings.review_overall.apply(discretize_rating)))

    return ratings


def get_neighbors(ratings:dict, # ratings submitted by each user or by each beer
                   min_rating_num:int=5 # at least this many ratings are required for a comparison
                      ):

    '''
    Compute rating-based similarity between every two pairs of users or pairs of beers

    '''

    #get all possible pairs
    pairs=list(combinations(list(ratings.keys()),2))

    sim=defaultdict(dict) # initialize the sim dictionary

    cnt=0

    N=len(pairs)

    print(f"Total Pairs: {N}")
    for id1,id2 in pairs: # for every entity pair

        cnt+=1

        if cnt%100000==0:
            print(cnt,'out of',N,' pairs evaluated')

        #get a set with all the discretized ratings (movie/user id, polarity tuples) for x1 and x2
        s1=set([(xid,pol) for xid,pol in ratings[id1].items()])
        s2=set([(xid,pol) for xid,pol in ratings[id2].items()])

        # check if both users/movies respect the lower bound
        if len(s1)<min_rating_num or len(s2)<min_rating_num: continue

        # get the union and intersection for these two users/movies
        union=s1.union(s2)
        inter=s1.intersection(s2)

        # compute user/movie sim via the jaccard coeff
        jacc=len(inter)/len(union)

        # remember the sim values
        sim[id1][id2]=jacc
        sim[id2][id1]=jacc

    # attach each user/movie to its neighbors, sorted by sim in descending order
    return {id_:sorted(sim[id_].items(),key=lambda x:x[1], reverse=True) for id_ in sim}