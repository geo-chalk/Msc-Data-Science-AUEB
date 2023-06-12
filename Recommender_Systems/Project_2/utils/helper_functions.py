import re
from string import digits
from random import random, sample
from itertools import combinations
from collections import defaultdict
from typing import List
from pprint import pprint

# ml
import numpy as np
import pandas as pd
from torch import Tensor


def preprocess(sentence):
    """
    Function to process a given sentence.
    INPUT: raw string
    OUTPUT: processed string
    """
    #convert the sentence to lower
    # nltk
    import nltk
    from nltk.stem import WordNetLemmatizer

    nltk.download('wordnet')
    nltk.download('stopwords')
    # initialize lemmatizer
    stemmer = WordNetLemmatizer()
    # define trans for digits
    remove_digits = str.maketrans('', '', digits)



    sentence = sentence.lower()

    # Remove underscores
    sentence = re.sub(r'[-_]', '', sentence)
    sentence = re.sub(r'_[A-Za-z0-9]+', ' ', sentence)
    sentence = re.sub(r'^ _\s+', ' ', sentence)

    # Remove usernames
    sentence = re.sub(r'@\w+', ' ', sentence)

    # Remove websites
    sentence = re.sub('https?://[A-Za-z0-9./]+', ' ', sentence)

    #remove all non words
    sentence = re.sub(r'\W', ' ', sentence)

    #remove all single characters
    sentence = re.sub(r'\b\w\b', ' ', sentence)

    # Remove numbers
    sentence = re.sub(r'[0-9]', ' ', sentence)
    sentence = sentence.translate(remove_digits)

    #remove multiple whitespaces
    sentence = re.sub(' +', ' ', sentence)

    # Split the sentence based on whitespaces (--> List of words)
    sentence = sentence.split()

    # Lemmatization
    sentence = [stemmer.lemmatize(word) for word in sentence]

    # Reconstruct the sentence by joining the words on each whitespace
    sentence = ' '.join(sentence)
    return sentence


def round_off_rating(number) -> float:
    """Round a number to the closest half integer. If nan return 5.5 (the average abv)"""
    if not np.isnan(number):
        return round(number * 2) / 2
    else:
        return 5.5


def sim_v2(title1:str,
           title2:str,
           beer_df:pd.DataFrame,
           weights:dict,
           sim_matrix:Tensor)->tuple:
    """Calculate the beer-to-beer similarity given two beers"""

    # get data
    b1 = beer_df.loc[beer_df.beer_name == title1]
    b2 = beer_df.loc[beer_df.beer_name == title2]

    # get indices
    b1_index = b1.index[0]
    b2_index = b2.index[0]


    scores=dict() # stores a the score for each factor from the weights dict

    # brewery_name jacard
    scores['brewery_name'] = len(set(b1.brewery_name).intersection(b2.brewery_name))/len(set(b1.brewery_name).union(b2.brewery_name))

    # beer_abv similarity
     # beer above 14 abv will be handled as the same.
    abv1 = min(b1.beer_abv.values[0], 14)
    abv2 = min(b2.beer_abv.values[0], 14)
    scores['beer_abv']= 1 - (abs(abv1 - abv2) / (min(beer_df.beer_abv.max(), 14) - beer_df.beer_abv.min()))

    # country jaccard
    scores['country'] = len(set(b1.country.values[0].split()).intersection(b2.country.values[0].split()))/len(set(b1.country.values[0].split()).union(b2.country.values[0].split()))

    # beer_style jaccard
    scores['beer_style'] = len(set(b1.beer_style.values[0].split()).intersection(b2.beer_style.values[0].split()))/len(set(b1.beer_style.values[0].split()).union(b2.beer_style.values[0].split()))

    # score jaccard
    scores['score'] = b1.score.values[0]/100

    # normalized rating
    scores['rating_mean'] = b1.rating_mean.values[0]/5

    # cosine sim for reviews
    scores['reviews']=sim_matrix[b1_index,b2_index].numpy()

    # create the sim dict
    factors={x:round(scores[x]*weights[x],2) for x in scores}

    # sort factors by sim
    sorted_factors=[factor for factor in sorted(factors.items(), key=lambda x:x[1],reverse=True) if factor[1]>0]

    # return overall score and explanations
    return round(np.sum(list(factors.values())),2),sorted_factors


def recommend(input_title:str,
              k:int,
              beer_df:pd.DataFrame,
              weights:dict,
              sim_matrix:Tensor
              ) -> list:
    """Recommend a beer based on similarity"""

    results={} # recommendations

    for candidate in beer_df.beer_name: # for each candidate

        #get the similarity and the explanation
        my_sim,my_exp=sim_v2(candidate, input_title, beer_df, weights, sim_matrix)

        #remember
        results[candidate]=(my_sim,my_exp)

    results.pop(input_title)

    # store, slice, return
    return sorted(results.items(),key=lambda x:x[1][0],reverse=True)[:k]


def user_like_threshold(reviews_df: pd.DataFrame,
                        user: str,
                        df: pd.DataFrame,
                        weights: dict,
                        sim_matrix: np.array,
                        _limit: int = 2000) -> float:
    """Compute the similarity threshold for a given user based on their past reviews."""

    print(f"Calculating user threshold for user: {user}")

    user_beer_positive = reviews_df.loc[(reviews_df.review_profilename == user) & (reviews_df.review_overall > 3.5)]

    # generate a random combination of length 2
    while True:
        try:
            comb = sample(list(combinations(user_beer_positive.beer_name.values, 2)), _limit)
            break
        except ValueError:
            _limit = _limit - 500

    sim_scores = []
    i = 0
    for c in comb:
        sim_scores.append(sim_v2(c[0],
                                 c[1],
                                 df,
                                 weights,
                                 sim_matrix)[0])
        i += 1

        if i == _limit:
            break

    print("Threshold is:", np.mean(sim_scores) + 1.5 * np.std(sim_scores))
    return np.mean(sim_scores) + 1.5 * np.std(sim_scores)  # threshold is mean + 1 std dev


def recommend_beers(reviews_df: pd.DataFrame,
                    beer_df: pd.DataFrame,
                    sim_matrix: np.array,
                    weights: dict,
                    user: str,
                    recnum_per_user: int,
                    neighbor_num: int,
                    liked_sample_size: int) -> None:

    # find user's movies
    user_info: pd.DataFrame = reviews_df.loc[reviews_df.review_profilename == user]
    user_beers: np.array = user_info.beer_name.values

    # find user's like threshold
    threshold = user_like_threshold(reviews_df=reviews_df,
                        user=user,
                        df=beer_df,
                        weights=weights,
                        sim_matrix=sim_matrix)



    #intialize likes and dislikes for this user
    likes=[]
    dislikes=[]


    #remembers previous recommendations
    recommended=set()

    for i in range(recnum_per_user): # for each recommendation to be made

        rec_beer=None # movie to be recommended

        radom_rec = ""
        # if the user has no known likes yet
        # and every 5 recommendations make a random one
        if len(likes)==0 or i % 5 == 0:

            # sample a random movie that has not been recommended before
            while rec_beer==None or rec_beer in recommended:
                rec_beer=beer_df.sample(n=1).beer_name.values[0]
            radom_rec = "Random Recommendation"

        else:
            # remembers candidate movies and maps them to a score
            # the score is equal to the sum of the similarity values with the
            # user's seed movies
            candidates=defaultdict(float)

            # get a sample of this user;s likes (For speed)
            sampled_likes=sample(likes, min(len(likes),liked_sample_size))

            # for each movie that has been liked by this user
            for liked_beer in likes:

                # find the top K most similar beers to this liked beer
                neighbors=recommend(liked_beer,neighbor_num,beer_df,weights,sim_matrix)


                # for each of the top-10 neighbors
                for neighbor,metrics in neighbors:
                    if neighbor not in recommended: # if the neighbor hasn't already been recommened, make it a candidate
                        candidates[neighbor]+=metrics[0] # update the score for this candidate


            if len(candidates)==0: # no candidates found

                #pick a random beer that has not been recommended already
                while rec_beer==None or rec_beer in recommended:
                    rec_beer=beer_df.sample(n=1).beer_name.values[0]
            else: # candidates found
                top_candidate = sorted(candidates.items(),key=lambda x:x[1],reverse=True)[0][0]
                #pick the top-scoring candidate
                rec_beer=beer_df.loc[beer_df.beer_name == top_candidate].beer_name.values[0]

        # remember the recommendation
        recommended.add(rec_beer)

        if rec_beer in user_beers:
            user_rating: float =user_info.loc[user_info.beer_name == rec_beer].review_overall.apply(lambda x: 'P' if float(x) > 3.5 else "N").values[0]

            if user_rating == 'P':
                likes.append(rec_beer)
                print('YES',rec_beer, f"(Already Rated: {user_rating})" ,radom_rec)
            else:
                dislikes.append(rec_beer)
                print('NO',rec_beer, f"(Already Rated: {user_rating})" ,radom_rec)
            continue

        found_seed=False # becomes true if the recommended beer is similar enough to one of the seed movies

        for beer in user_beers: # for each seed beer

            #compute the sim between the seed beer and the recommended beer
            val=sim_v2(rec_beer,
                   beer,
                   beer_df,
                   weights,
                   sim_matrix)[0]

            # if the sim is over the like threshold for this user
            if val>threshold:
                found_seed=True
                break

        if found_seed: # similar seed found, the user will like this movie
            likes.append(rec_beer)
            print('YES', rec_beer, radom_rec)
        else:
            dislikes.append(rec_beer)
            print('NO', rec_beer, radom_rec)


    print(f'\n\nTotal Likes out of {recnum_per_user}:', len(likes),'\n\n-----------------------\n')
