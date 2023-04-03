import pandas as pd
import tomotopy as tp
from .Loggers import BaseLogger

logger = BaseLogger().logger


def setup_LDA(docs: dict,
              k_range: tuple,
              k_step: int,
              iteration_range: tuple,
              iterations_step: int,
              top_n: int,
              reviews: pd.DataFrame,
              verbose: int = 0 # set the level of verbose, 0: best model printed, 1: categories
              ) -> list:

    """Find the bect cobination of k, iterations and step in order to maximize Log-likelihiood"""
    min_likelihood = -100
    for k in range(k_range[0], k_range[1], k_step):
        #new LDA model
        lda = tp.LDAModel(k=k)

        for doc in docs:
            lda.add_doc(docs[doc])

        #train LDA model
        for i in range(iteration_range[0], iteration_range[1], iterations_step):
            lda.train(iterations_step)
            logger.info('Iteration: {}\tLog-likelihood: {}\tk: {}'.format(i, lda.ll_per_word, k))
            if lda.ll_per_word > min_likelihood:
                min_data = (i, lda.ll_per_word, k)
                min_likelihood = lda.ll_per_word
                best_lda = lda
    print(f"Best Model: k={min_data[2]}, iterations={min_data[0]}, Log-likelihood={min_data[1]:.2f}")

    groups: list = []
    #print topic info
    for k in range(min_data[2]):

        topk_words=[pair[0] for pair in best_lda.get_topic_words(k, top_n=top_n)]

        titles: list =[(int(label[:-1]), reviews[reviews.beer_id==int(label[:-1])].beer_name.array[0],label[-1]) for label in topk_words]

        # print top categories
        if verbose > 0:
            print(k)
            for title in titles[:10]:
                print(title)
            print('--------------------------------------')
            print()

        groups.append(titles)

    return groups


def recommend_lda(groups: list,
                  user: int,
                  rec_num: int,
                  _user_ratings: dict,
                  _beer_mapping: dict):

    # setup user data
    previous_ratings = {x: y for x, y in _user_ratings[user]}

    # metrics for total recommendations
    best_recommendations = []
    best_score: float = 0


    for i, category in enumerate(groups):

        # category metrics
        recommendations: list = []
        already_rated = {}
        cnt = 0

        # for each category keep positive reviews. See how many the user has rated
        for beer_id, beer, score in category:  # for each beer


            rat = previous_ratings.get(beer_id, None)
            if rat:  # beer already rated
                already_rated[beer] = rat  # store the rating
                continue

            # only recommend positive beers
            if score == 'P':
                recommendations.append((beer_id, beer))
                cnt += 1  # one more recommendation

            if cnt == rec_num:
                break

        print(f"Group: {i + 1}")
        if already_rated:
            score: float = list(already_rated.values()).count("P")/len(already_rated.values())
            print("Positive ratio:", f'{score*100:.2f}%')
            print("Already Rated number of beers:", f'{len(already_rated.values())}', end="\n\n")
            # keep best scores
            if score > best_score:
                best_recommendations = recommendations
        else:
            print("No beers already rated in the group")

    return best_recommendations
