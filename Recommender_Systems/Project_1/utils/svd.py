import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

def recommend(uid:int,
              reviews:pd.DataFrame,
              U:np.ndarray,
              sigma:np.ndarray,
              Vt:np.ndarray,
              user_means:np.ndarray,
              rec_num:int,
              ratings_matrix:pd.DataFrame
             ):

    #get all the ratings by this user
    my_ratings=reviews[["user_id", "beer_id", "review_overall"]][reviews.user_id==uid]

    # beers df
    beers_df = reviews[["beer_id", "beer_name", "beer_style"]].drop_duplicates()

    #zip the ratings into a dict
    already_rated=dict(zip(my_ratings.beer_id,my_ratings.review_overall))

    #predict the rating of this user for all movies
    predicted_ratings=np.dot(np.dot(U[uid-1], sigma),Vt)+user_means[uid-1]

    # get the indexes of the ratings sorted in descending order
    indexes_sorted=np.argsort(predicted_ratings)[::-1]

    # get the scores for the sorted indexes

    predicted_ratings_sorted=predicted_ratings[indexes_sorted]

    # get the original movie indexes
    original_indexes_sorted=[ratings_matrix.columns[i] for i in indexes_sorted]

    pred_dict=dict(zip(original_indexes_sorted,predicted_ratings_sorted))

    rec_set=set()# set of movie ids to be recommended

    for mid in original_indexes_sorted: # for each movie id
        if mid not in already_rated: # movie has not already been rated
            rec_set.add(mid) # add to the set

            if len(rec_set)==rec_num:break

    # make a data frame with only the recommended movies
    rec_df=pd.DataFrame(beers_df[beers_df.beer_id.isin(rec_set)])

    #add the predicted rating as a new column
    rec_df['predicted_rating']=rec_df['beer_id'].map(pred_dict)

    #sort the df by the new col
    rec_df=rec_df.sort_values(['predicted_rating'], ascending=False)

    return rec_df




def validate(uid:int,
              reviews:pd.DataFrame,
              U:np.ndarray,
              sigma:np.ndarray,
              Vt:np.ndarray,
              user_means:np.ndarray,
              ratings_matrix:pd.DataFrame
             ):

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

    actual,pred=[],[]
    for mid in already_rated: # movie has already been rated
        actual.append(already_rated[mid])
        pred.append(pred_dict[mid])

    return mean_squared_error(actual,pred,squared=False)