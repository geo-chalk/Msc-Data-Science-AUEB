import numpy as np
import pandas as pd


def recommend(uid:int,
              reviews:pd.DataFrame,
              U:np.ndarray,
              sigma:np.ndarray,
              Vt:np.ndarray,
              user_means:np.ndarray,
              rec_num:int,
              ratings_matrix:pd.DataFrame,
              beer_mapping: dict
             ):

    # get all the ratings by this user
    my_ratings = reviews[["user_id", "beer_id", "review_overall", "rating"]][reviews.user_id == uid]

    # beers df
    beers_df = reviews[["beer_id", "beer_name"]].drop_duplicates()

    # zip the ratings into a dict
    user_ratings = dict(zip(my_ratings.beer_id, my_ratings.rating))

    # predict the rating of this user for all movies
    predicted_ratings = np.dot(np.dot(U[uid - 1], sigma), Vt) + user_means[uid - 1]

    # get the indexes of the ratings sorted in descending order
    indexes_sorted = np.argsort(predicted_ratings)[::-1]

    # get the scores for the sorted indexes

    predicted_ratings_sorted = predicted_ratings[indexes_sorted]

    # get the original my_ratings indexes
    original_indexes_sorted = [ratings_matrix.columns[i] for i in indexes_sorted]

    pred_dict = dict(zip(original_indexes_sorted, predicted_ratings_sorted))

    rec_set = set()  # set of beer ids to be recommended

    already_rated = {}
    for beer in original_indexes_sorted:  # for each beer id
        if beer not in user_ratings:  # beer has not already been rated
            rec_set.add(beer)  # add to the set

            if len(rec_set) == rec_num: break
        else:
            already_rated[beer_mapping.get(str(beer))] = user_ratings.get(beer)

    # make a data frame with only the recommended movies
    rec_df = pd.DataFrame(beers_df[beers_df.beer_id.isin(rec_set)])

    # add the predicted rating as a new column
    rec_df['predicted_rating'] = rec_df['beer_id'].map(pred_dict)

    # sort the df by the new col
    rec_df = rec_df.sort_values(['predicted_rating'], ascending=False)
    rec_df["pred_rating_discr"] = rec_df.apply(lambda x: "P" if x["predicted_rating"] > 3.5 else "-", axis=1)

    return rec_df, already_rated


def initialize_svd(reviews: pd.DataFrame) -> tuple:
    """Prepare the table that will be used in the SVD calculation"""
    # convert the ratings frame to a user X movies matrix
    ratings_matrix = reviews.sort_values(by=["user_id", "beer_id"])[
        ["user_id", "beer_id", "review_overall"]].drop_duplicates().pivot_table(index='user_id', columns='beer_id',
                                                                                values='review_overall').fillna(
        reviews.review_overall.mean())

    # convert the matrix into an array
    ratings_np = ratings_matrix.values
    # compute the average rating per user
    user_means = np.mean(ratings_np, axis=1)
    # subtract the mean from each rating
    ratings_np_centered = ratings_np - user_means.reshape(-1, 1)

    # unique user and movie num
    user_num = reviews.user_id.unique().shape[0]
    movie_num = reviews.beer_id.unique().shape[0]
    sparsity = round(1.0 - len(reviews) / float(user_num * movie_num), 3)

    return ratings_np_centered, user_means, ratings_matrix


def validate(uid:int,
             reviews: pd.DataFrame,
             U: np.ndarray,
             sigma: np.ndarray,
             Vt: np.ndarray,
             user_means: np.ndarray,
             ratings_matrix: pd.DataFrame
             ) -> tuple:

    #get all the ratings by this user
    my_ratings=reviews[["user_id", "beer_id", "review_overall"]][reviews.user_id==uid]

    # beers df
    beers_df = reviews[["beer_id", "beer_name", "beer_style"]].drop_duplicates()

    #zip the ratings into a dict
    already_rated=dict(zip(my_ratings.beer_id, my_ratings.review_overall))

    #predict the rating of this user for all movies
    predicted_ratings=np.dot(np.dot(U[uid-1], sigma),Vt)+user_means[uid-1]

    # get the indexes of the ratings sorted in descending order
    indexes_sorted=np.argsort(predicted_ratings)[::-1]

    # get the scores for the sorted indexes
    predicted_ratings_sorted=predicted_ratings[indexes_sorted]

    # get the original movie indexes
    original_indexes=[ratings_matrix.columns[i] for i in indexes_sorted]

    pred_dict=dict(zip(original_indexes,predicted_ratings_sorted))

    actual, pred=[],[]
    for mid in already_rated: # movie has already been rated
        actual.append(already_rated[mid])
        pred.append(pred_dict[mid])

    count = 0
    for act, prd in zip(actual, pred):
        if act > 3.5 and prd > 3.5:
            count += 1

    return count, len(actual)
