import pandas as pd
from datasketch import MinHash, MinHashLSH
from typing import List


class Esim:

    def __init__(self,
                 reviews_df: pd.DataFrame,  # reviews_df
                 beer_id_col: str,  # name of the beer id col
                 user_id_col: str,  # name of the user id col
                 beer_mapping: dict,  # maps each beer_id to the corresponding name
                 user_mapping: dict,  # maps each user_id to the username
                 nrows_beers: int = None,  # beer rows to read
                 nrows_ratings: int = None  # rating rows to read
                 ):

        # read movies
        self.reviews_df = reviews_df

        print('Data loaded')

        # remember the user and movie id cols
        self.user_id_col = user_id_col
        self.beer_id_col = beer_id_col

        self.beer_mapping = beer_mapping
        self.user_mapping = user_mapping

    @staticmethod
    def discretize_rating(rating: float) -> str:
        """Converts a given float rating to a string value"""
        polarity = 'A'  # average

        if rating < 3:
            polarity = 'N'  # negative
        elif rating > 3:
            polarity = 'P'  # positive

        return polarity

    def load_ratings(self, focus: List[str]) -> dict:

        """
        Loads all the ratings submitted by each user or all ratings submitted for a beer (based on focus)

        Returns:
            a dictionary that maps each user to a second dict that maps beers to discretized ratings

            OR

            a dictionary that maps each beer to a second dict that maps users to discretized ratings

        """

        self.reviews_df.set_index(focus[0])

        distinct_ids = set(self.reviews_df[focus[0]])  # get all distinct users

        ratings = {}  # store ratings per entity

        for id_ in progressbar(distinct_ids, "Loading ratings: ", 60):  # for each user

            # get the infro for every rating submitted for this user or for this movie
            my_ratings = self.reviews_df[self.reviews_df[focus[0]] == id_][[focus[1], 'review_overall']]

            # discretize the ratings and attach them to the user or to the movie
            ratings[id_] = set(zip(my_ratings[focus[1]], my_ratings.review_overall.apply(self.discretize_rating)))

        return ratings

    def index(self,
              focus: str,  # determines whether a user-based or beer-based index will be made
              jaccard_threshold: float = 0.2,  # lower sim bound for the index
              index_weights=(0.2, 0.8),  # false pos and false neg weights
              num_perm: int = 1000,  # number of random permutations
              min_num: int = 5):  # entities with less than this many ratings are ignored

        """
        Creates a user-based or beer-based LSH index
        """

        # create the index
        index = MinHashLSH(threshold=jaccard_threshold, weights=index_weights, num_perm=num_perm)

        # remember the hashes of each entity
        hashes = {}

        if focus == 'beer':  # beer
            self.beer_ratings = self.load_ratings([self.beer_id_col, self.user_id_col])
            print('beer ratings processed')

            self.beer_index, self.beer_hashes, self.beer_threshold, ratings = index, hashes, jaccard_threshold, self.beer_ratings
        else:  # users
            self.user_ratings = self.load_ratings([self.user_id_col, self.beer_id_col])
            print('user ratings processed')

            self.user_index, self.user_hashes, self.user_threshold, ratings = index, hashes, jaccard_threshold, self.user_ratings

        cnt = 0

        N = len(ratings)  # total number of entities to index

        for eid, my_ratings in ratings.items():  # for all entities

            cnt += 1

            if cnt % 500 == 0: print(cnt, 'out of', N, 'entities indexed.', end='\r', file=sys.stdout, flush=True)

            if len(ratings) < min_num:
                continue  # not enough ratings for this entity

            rating_hash = MinHash(num_perm=num_perm)  # create a new hash for this entity

            for id_, pol in my_ratings:  # for each rating associated with this entity
                s = str(id_) + '_' + pol  # create a string

                rating_hash.update(s.encode('utf8'))  # add the string to the hash for this entity

            hashes[eid] = rating_hash  # remember the hash for this entity

            index.insert(eid, rating_hash)  # index the entity based on its hash

        print(focus + '-based index created')

    def jaccard(self, s1: set, s2: set):
        '''
        Computes the jaccard coeff between two sets s1 and s2
        '''
        return len(s1.intersection(s2)) / len(s1.union(s2))

    def get_neighbors(self,
                      focus: str,  # 'beer' for beers, 'usr' for users
                      eid: int,  # entity whose neighbors are to be retrieved
                      ):
        '''
        Uses the index to find and return the neighbors with a certain sim threshold for a given entity.
        '''
        if focus == 'beer':
            index, ratings, hashes, threshold = self.beer_index, self.beer_ratings, self.beer_hashes, self.beer_threshold
        else:
            index, ratings, hashes, threshold = self.user_index, self.user_ratings, self.user_hashes, self.user_threshold

        result = index.query(hashes[eid])  #

        neighbors = []  # stores neighbors

        for nid in result:  # for each candidate neighbor

            if nid == eid: continue  # ignore the entity itself

            jacc = self.jaccard(ratings[nid], ratings[eid])  # compute jaccard
            if jacc >= threshold:  # if the threshold is respected, add
                neighbors.append((nid, jacc))

        return neighbors
