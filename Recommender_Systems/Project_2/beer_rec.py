# python
from typing import Optional
from pathlib import Path
import pickle

# fast api
from fastapi import FastAPI, status
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

# ml
import pandas as pd
import numpy as np
import torch

# custom
from utils.Loggers import BaseLogger
from utils.helper_functions import *


logger = BaseLogger().logger

app = FastAPI()
df: Optional[pd.DataFrame] = None
sim_matrix: Optional[torch.Tensor] = None
reviews_df = None


class Weights(BaseModel):
    brewery_name: float = 0.5
    beer_abv: float = 1
    country: float = 0.2
    beer_style: float = 1
    score: float = 1
    rating_mean: float = 1
    reviews: float = 1


weights = Weights()


@app.get("/get_weights")
async def get_weights():
    return weights


@app.put("/update_weights/", response_model=Weights)
async def update_weights(weight: Weights) -> JSONResponse:
    global weights

    logger.info("Updating weights")
    for k, v in weight.dict().items():

        if not 0 <= v <= 1:
            return JSONResponse({"status": "FAILURE",
                                 "message": "Weight Values should be between 0 and 1"})
    weights = weight
    logger.info("Weights Updated")
    return JSONResponse({"status": "SUCCESS",
                         "message": "Weights changed"})

@app.on_event("startup")
@app.get("/load_configurations")
async def load_configurations() -> JSONResponse:
    global df
    global sim_matrix
    global reviews_df

    logger.info("Caching Configurations")

    try:
        # --- load dataframe --- #
        df = pd.read_csv("aggregated_reviews_small.csv",
                         usecols=['brewery_id', 'brewery_name',
                                  'beer_id', 'beer_name', 'beer_abv',
                                  'country', 'style', 'score',
                                  'rating_mean', 'rating_std'])

        # handle missing scores
        df.score = df.score.apply(lambda x: np.nan if "Needs more ratings" in x else x)
        score_mean: int = int(df.score.astype(float).mean())
        df.score = df.score.fillna(score_mean).astype(int)

        # round abv
        df.beer_abv = df.beer_abv.apply(lambda x: round_off_rating(x))

        # rename style column
        df.rename(columns={'style': 'beer_style'}, inplace=True)
        logger.info("aggregated_reviews_small.csv loaded")
    except:
        return JSONResponse({"status": "FAILURE",
                             "message": "Failed to load aggregated_reviews_small.csv"})

    try:
        # --- load sim_matrix --- #
        sim_matrix_path: Path = Path('pkl_files') / "sim_matrix.pkl"

        # Load pkl sim_matrix file
        with sim_matrix_path.open('rb') as f:
            sim_matrix = pickle.load(f)
        logger.info("./pkl_files/sim_matrix.pkl loaded")
    except:
        return JSONResponse({"status": "FAILURE",
                             "message": "Failed to load ./pkl_files/sim_matrix.pkl"})

    try:
        # --- load beer reviews --- #
        reviews_df = pd.read_csv("beer_reviews.csv", usecols=['review_profilename', 'brewery_id', 'brewery_name',
                                                              'review_overall', 'beer_style', 'beer_name',
                                                              'beer_abv', 'beer_beerid'])

        # only keep scrapped beers
        reviews_df = reviews_df.loc[reviews_df.beer_beerid.isin(df.beer_id.drop_duplicates().values)]
        logger.info("beer_reviews.csv loaded")
    except:
        return JSONResponse({"status": "FAILURE",
                             "message": "Failed to load beer_reviews.csv"})


    return JSONResponse({"status": "SUCCESS",
                         "message": "Configurations Loaded"})


@app.get("/recommend_beer")
async def recommend_beer(beer: str, num_rec: int = 5) -> JSONResponse:
    rec = {}
    try:
        recommendations = recommend(beer, num_rec, df, weights.dict(), sim_matrix)
        for r in recommendations:
            rec_beer = df.loc[df.beer_name == r[0]]
            brewery_id = rec_beer.brewery_id.values[0]
            beer_id = rec_beer.beer_id.values[0]
            rec[r[0]] = {"brewery_name": rec_beer.brewery_name.values[0],
                       "beer_style": rec_beer.beer_style.values[0],
                       "beeradvocate_link": f"https://www.beeradvocate.com/beer/profile/{brewery_id}/{beer_id}/"
                       }
    except IndexError:
        return JSONResponse({"status": "FAILURE", "message": f"Please make sure that the beer name {beer} is valid."})

    return JSONResponse({"Recommendations": rec})


@app.get("/health")
async def health() -> JSONResponse:

    content = {"aggregated_reviews_small.csv": status.HTTP_400_BAD_REQUEST,
               "./pkl_files/sim_matrix.pkl": status.HTTP_400_BAD_REQUEST,
               "beer_reviews.csv": status.HTTP_400_BAD_REQUEST}

    if isinstance(df, pd.DataFrame):
        content["aggregated_reviews_small.csv"] = status.HTTP_200_OK

    if isinstance(sim_matrix, torch.Tensor):
        content["./pkl_files/sim_matrix.pkl"] = status.HTTP_200_OK

    if isinstance(reviews_df, pd.DataFrame):
        content["beer_reviews.csv"] = status.HTTP_200_OK

    if not all([True if i == status.HTTP_200_OK else False for i in list(content.values())]):
        content["status"] = "DOWN"
    else:
        content["status"] = "UP"

    return JSONResponse(content)
