from .Loggers import BaseLogger
from dataclasses import dataclass
from typing import List, Optional, Union, Any
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import pandas as pd
from .esim import Esim
import csv
import numpy as np

@dataclass
class BeerReview(object):
    index: int
    brewery_id: str
    brewery_name: str
    review_time: datetime.timestamp
    review_overall: float
    review_aroma: float
    review_appearance: float
    review_profilename: str
    beer_style: str
    review_palate: float
    review_taste: float
    beer_name: str
    beer_abv: float
    beer_beerid: int
    user_id: Optional[Union[int, None]] = None


class ReviewReader(BaseLogger):
    """Read reviews based on an input file"""
    reviews: List[Any] = []

    def __init__(self, file_path: str,
                 user_reviews_threshold: int = 10,
                 beer_reviews_threshold: int = 10,
                 subset: float = 1.0,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.user_reviews_threshold = user_reviews_threshold
        self.beer_reviews_threshold = beer_reviews_threshold
        self.subset = subset
        self.reviews_df: Optional[pd.DataFrame] = None

        # initialize users and beers dict
        self.users: defaultdict = defaultdict(int)  # to keep track of user reviews counts
        self.beers: defaultdict = defaultdict(int)  # to keep track of beer reviews counts

        # initialize mappings
        self.user_mapping: defaultdict = defaultdict(str)
        self.beer_mapping: defaultdict = defaultdict(str)

    @property
    def input_file(self) -> Path:
        """
        Creates a Path object containing the input file.
        Raises an exception if the file doesn't exist

        Returns:
            Path object
        """
        input_file: Path = Path(self.file_path)
        if not input_file.is_file():
            self.logger.error(f"{input_file.name} file doesn't exist.")

        return input_file

    @property
    def valid_users(self) -> list:
        """Returns that have more than user_reviews_threshold reviews"""
        return [user for user, total_ratings in self.users.items() if total_ratings >= self.user_reviews_threshold]

    @property
    def valid_beers(self) -> list:
        """Returns that have more than user_reviews_threshold reviews"""
        return [beer for beer, total_ratings in self.beers.items() if total_ratings >= self.beer_reviews_threshold]

    @staticmethod
    def make_array(_review: BeerReview):
        """Select the necessary columns needed from the BeerReview object
        user_id, review_profilename
        beer_beerid, review_overall
        review_aroma, review_appearance, review_taste, review_palate"""

        return [_review.user_id, _review.review_profilename,
                _review.beer_beerid, _review.beer_name, _review.beer_style,
                _review.review_overall, _review.review_aroma, _review.review_appearance, _review.review_taste,
                _review.review_palate,
                _review.brewery_id]

    @property
    def train(self) -> pd.DataFrame:
        return self.reviews_df.iloc[:int((self.reviews_df.shape[0] * 0.3)), :]

    @property
    def test(self) -> pd.DataFrame:
        return self.reviews_df.iloc[int((self.reviews_df.shape[0] * 0.3)):, :]

    @property
    def test_users(self) -> np.array:
        np.random.seed(42)
        _users = [2123, 1667, 1722, 1706, 1245, 2712, 1332, 1030]
        sample = np.random.choice(np.where(( self.reviews_df.groupby("user_id")["user_id"].count() > 500) & (
        ( self.reviews_df.groupby("user_id")["user_id"].count() < 1000)))[0], 100)

        return np.setdiff1d(sample, np.array(_users))


    def filter_reviews(self) -> None:
        """Filters the reviews dataframe to keep users based on defined thresholds"""

        # filter users
        self.reviews_df = self.reviews_df.loc[(self.reviews_df.user_name.isin(self.valid_users))
                                              & (self.reviews_df.beer_id.isin(self.valid_beers))
                                              & (self.reviews_df.user_name != "")]

    def subset_reviews(self) -> None:
        """Take a subset of the reviews for training purposes"""
        self.reviews_df = self.reviews_df.iloc[:int((self.reviews_df.shape[0] * self.subset)), :]

    def discretize_ratings(self) -> None:
        """Discretize Ratings"""
        # discretize ratings
        self.reviews_df["rating"] = self.reviews_df.apply(lambda x: Esim.discretize_rating(x["review_overall"]), axis=1)

    def read_reviews(self) -> pd.DataFrame:
        """
        Read the reviews based on the input file. Returns a list of reviews.        """
        with open(self.input_file, encoding="utf8") as f:

            self.logger.info(f"Loading {self.input_file}")

            # initialize user_id
            user_id: dict = {}
            _id: int = 0

            for i, row in enumerate(csv.DictReader(f)):

                # add user_id and user_mapping
                if user_id.get(row["review_profilename"].strip()) is None:
                    user_id[row["review_profilename"].strip()] = _id
                    self.user_mapping[id] = row["review_profilename"].strip()
                    _id += 1

                # add beer_mapping
                if not self.beer_mapping.get(row["beer_beerid"]):
                    self.beer_mapping[row["beer_beerid"]] = row["beer_name"]

                # create a review object
                review: BeerReview = BeerReview(
                    int(row["index"]) if row["index"].isnumeric() else None,
                    row["brewery_id"],
                    row["brewery_name"].strip(),
                    datetime.fromtimestamp(int(row["review_time"])),
                    float(row["review_overall"]),
                    float(row["review_aroma"]),
                    float(row["review_appearance"]),
                    row["review_profilename"].strip(),
                    row["beer_style"].strip(),
                    row["review_palate"],
                    row["review_taste"],
                    row["beer_name"],
                    row["beer_abv"],
                    int(row["beer_beerid"]),
                    user_id[row["review_profilename"]])

                # add the review object to the total reviews
                self.reviews.append(self.make_array(review))

                # Keep user count
                self.users[review.review_profilename] += 1
                self.beers[review.beer_beerid] += 1

                if i % 300000 == 0 and i != 0:
                    self.logger.info(f"{i} reviews loaded.")

        self.logger.info(f"All reviews loaded. Total reviews: {len(self.reviews)}")
        f.close()

        # Convert to Pandas Dataframe
        self.reviews_df = pd.DataFrame(self.reviews,
                                       columns=["user_id", "user_name",
                                                "beer_id", "beer_name", "beer_style",
                                                "review_overall", "review_aroma", "review_appearance", "review_taste",
                                                "review_palate",
                                                "brewery_id"])

        self.reviews_df.drop_duplicates(inplace=True)
        self.filter_reviews()
        self.subset_reviews()
        self.discretize_ratings()

        self.logger.info(f"Processing completed.")

        return self.reviews_df
