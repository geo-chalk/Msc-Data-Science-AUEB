import sys
from .esim import Esim
from collections import defaultdict
from typing import Union, Optional
import pandas as pd
import pickle
from .Loggers import BaseLogger

logger = BaseLogger().logger


def progressbar(it, prefix="", size=60, out=sys.stdout, print_every=100):
    count = len(it)

    def show(j):
        if j % print_every == 0 or j == count:
            x = int(size*j/count)
            print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count}", end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)


def recommend_mb(indexer:Esim,
                 user:int,  # user to receive the recs
                 rec_num:int,# number of recs to make
                 verbose: int = 0  # set the level of verbose, 0 means no output, 1 suggestions, 2 everything
                ) -> dict:

    '''
    Beer-based recommendations

    For each user, get the list of all the beers they have rated positively .
    For each of these beers, find its most similar beers

    Every candidate Beer gets a +1 if it appears in the top-k neighbors of a Beer
    that the user has rated positively.

    The +1 vote is scaled based on the sim of the candidate to the Beer that the user liked.

    '''

    # get all the beers rated by this user
    my_ratings=indexer.reviews_df[indexer.reviews_df.user_id==user][['beer_id', 'review_overall']]

    #convert them to a dict
    my_ratings=dict(zip(my_ratings.beer_id, my_ratings.review_overall.apply(indexer.discretize_rating)))

    # votes for each Beer
    votes=defaultdict(int)

    for mid, pol in my_ratings.items(): # for each beer rated by this user

        if pol!='P': continue  # only consider positively rated beers

        mid_neighbors=indexer.get_neighbors('beer',mid) # find the neighbors

        for neighbor,sim_val in mid_neighbors: # for each neighbor

            if verbose >= 2: print('neighbor', neighbor)

            votes[neighbor]+=sim_val # add a scaled vote

    # sort candidates by their scaled votes
    srt=sorted(votes.items(),key=lambda x:x[1], reverse=True)

    if verbose >= 1: print('\nI suggest the following beers because they are similar to the beers you already like:\n')

    cnt=0

    already_rated={}

    for beer, score in srt:

        title=indexer.beer_mapping.get(str(beer))

        rat=my_ratings.get(beer,None)

        if rat:
            already_rated[title]=rat
            continue

        cnt+=1

        if verbose >= 1:
            print(beer, title,  f"{score:.2f}")

        if cnt==rec_num:break

    if verbose >= 2: print('\n',already_rated)
    return already_rated


def recommend_ub(indexer: Esim,
                 user: int,  # user to receive the recs
                 rec_num: int,  # number of beers to recommend
                 verbose: int = 0  # set the level of verbose, 0 means no output, 1 suggestions, 2 everything
                 ) -> dict:
    '''
    Delivers user-based recommendations. Given a specific user:
    - find the user's neighbor_num most similar users
    - Go over all the beers rated by all neighbors
    - Each beer gets +2 if a neighbor liked it, -2 if a neighbor didn't like it, -1 if  neighbor was neutral
    - +2,-1,and -2 are scaled based on user sim
    - Sort the beers by their scores in desc order
    - Go over the sorted beer list. If the user has already rated the beer, store its rating. Otherwise print.

    '''

    neighbors = indexer.get_neighbors('usr', user)

    votes = defaultdict(int)  # count the votes per beer

    for neighbor, sim_val in neighbors:  # for each neighbor

        if verbose >= 2: print('neighbor', neighbor)

        for mid, pol in indexer.user_ratings[neighbor]:  # for each beer rated by this neighbor

            if pol == 'P':  # positive neighbor rating
                votes[mid] += 2 * sim_val
            elif pol == 'N':  # negative
                votes[mid] -= 2 * sim_val
            else:  # average
                votes[mid] -= 1 * sim_val

    # sort the beers in desc order
    srt = sorted(votes.items(), key=lambda x: x[1], reverse=True)

    if verbose >= 1: print('\nI suggest the following beers because they have received positive ratings\n'
                           'from users who tend to like what you like:\n')

    cnt = 0  # count number of recommendations made

    already_rated = {}

    previous_ratings = {x: y for x, y in indexer.user_ratings[user]}

    for beer, score in srt:  # for each beer

        try:
            title = indexer.beer_mapping.get(str(beer))  # get the title
        except KeyError:
            title = 'placeholder'

        rat = previous_ratings.get(beer, None)

        if rat:  # beer already rated
            already_rated[title] = rat  # store the rating
            continue

        cnt += 1  # one more recommendation
        if verbose >= 1: print(beer, title, f"{score:.2f}")  # print

        if cnt == rec_num: break  # stop once you 've made enough recommendations

    if verbose >= 2: print('\n', already_rated)

    return already_rated


def load_indexer(focus: Optional[str] = None,
                 reviews: Optional[pd.DataFrame] = None,
                 beer_mapping: Optional[dict] = None,
                 user_mapping: Optional[dict] = None,
                 beer_id_col: Optional[str] = 'beer_id',
                 user_id_col: Optional[str] = 'user_id',
                 indexer_path: Optional[str] = None) -> Esim:
    """
    Loads the indexer object classes for beer_based and user_based reviews.
    Attempts to use the
        - indexer_beer.pkl
        - indexer_user files.pkl
    files from the dict. Specify absolute path if needed


    Args:
        focus: user based on beer based. Supported {usr, beer]
        reviews: dataframe with the reviews
        beer_id_col: the name of the beer_id column
        user_id_col: the name of the user_id column
        beer_mapping: dictionary with {beer_id : name}
        user_mapping: dictionary with {user_id : name}
        indexer_path: the pkl file path to load

    Returns:
        Esim class
    """

    try:

        logger.info(f"Trying to load {indexer_path} file.")
        with open(indexer_path, 'rb') as handle:
            indexer = pickle.load(handle)
            logger.info(f"{indexer_path} file loaded.")

    except (FileNotFoundError, EOFError) as e:

        logger.warning(f"{indexer_path} file doesn't exist. Proceeding to calculate.")
        indexer=Esim(reviews_df=reviews,
                     beer_id_col=beer_id_col, user_id_col=user_id_col,
                     beer_mapping=beer_mapping, user_mapping=user_mapping)

        indexer.index(focus, jaccard_threshold=0.1)

        logger.info(f"Saving {indexer_path} file.")
        with open(indexer_path, 'wb') as handle:
            pickle.dump(indexer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"{indexer_path} file saved.")

    handle.close()


    return indexer
