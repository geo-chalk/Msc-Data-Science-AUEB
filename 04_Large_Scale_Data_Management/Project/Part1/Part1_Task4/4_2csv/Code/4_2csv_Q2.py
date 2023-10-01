from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, DoubleType
import time

# Q2: For the movie ”Cesare deve morire” find and print 
# the movies id and then search 
# how many users rated the movie and 
# what the average rating was?

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark CSV query 2 execution") \
    .getOrCreate()
    
movie_schema = StructType([
         StructField("movie_id", IntegerType(), True),
         StructField("name", StringType(), True),
         StructField("description", StringType(), True),
         StructField("year", StringType(), True),
         StructField("duration", IntegerType(), True),
         StructField("cost", IntegerType(), True),
         StructField("revenue", IntegerType(), True),
         StructField("rating", DoubleType(), True)])

movies_df = sc.read.format('csv').options(header='false').schema(movie_schema).load("hdfs://master:9000/home/user/project/csv/movies.csv") 
movies_df.registerTempTable("movies")

rating_schema = StructType([
         StructField("user_id", IntegerType(), True),
         StructField("movie_id", IntegerType(), True),
         StructField("rating", DoubleType(), True),
         StructField("timestamp", StringType(), True)])

ratings_df = sc.read.format('csv').options(header='false').schema(rating_schema).load("hdfs://master:9000/home/user/project/csv/ratings.csv") 
ratings_df.registerTempTable("ratings")

#find movie_id of "Cesare deve morire"
query = "SELECT movies.movie_id FROM movies WHERE movies.name == 'Cesare deve morire'"
movie_id = sc.sql(query).collect()

#find movie_id of "Cesare deve morire"
query = "SELECT ratings.movie_id, COUNT(ratings.user_id) AS total_user_rated, AVG(ratings.rating) AS average_rating FROM ratings WHERE ratings.movie_id == {} group by ratings.movie_id".format(movie_id[0].movie_id)
movie = sc.sql(query).collect()

print("The movie ID of 'Cesare deve morire' is:", movie_id[0].movie_id)
print("The 'Cesare deve morire' movie was rated by", movie[0].total_user_rated, "users and has an average rating of", movie[0].average_rating)

# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q2: ')
    fd.write(str(time_avg))
    fd.write('\n')