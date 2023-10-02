from pyspark.sql import SparkSession
from pyspark.sql.functions import avg

# Q2: For the movie Cesare deve morire find and print 
# the movies id and then search 
# how many users rated the movie and 
# what the average rating was?

sc = SparkSession \
    .builder \
    .appName("Dataframe query 2 execution") \
    .getOrCreate()

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
ratings_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/ratings.parquet')

#find movie_id of "Cesare deve morire"
movie_id = movies_df.filter((movies_df.name == "Cesare deve morire"))

#find many users rated the movie and what the average rating 
movie_rating = ratings_df.filter((ratings_df.movie_id == movie_id.first()[0]))
users = movie_rating.count()
avg_rating = movie_rating.select(avg('rating')).collect()[0][0]

#print result
print("The movie ID of 'Cesare deve morire' is:", movie_id.first()[0])
print("The 'Cesare deve morire' movie was rated by", users , "users and has an average rating of", avg_rating)