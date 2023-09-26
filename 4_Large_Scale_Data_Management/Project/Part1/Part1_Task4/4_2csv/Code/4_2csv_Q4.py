from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType,StringType, DoubleType
import time

# Q4: Find and print the most popular Comedy movies for every year after 1995

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark CSV query 4 execution") \
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

movie_genre_schema = StructType([
         StructField("movie_id", IntegerType(), True),
    	 StructField("genre", StringType(), True)])

movie_genres_df = sc.read.format('csv').options(header='false').schema(movie_genre_schema).load("hdfs://master:9000/home/user/project/csv/movie_genres.csv") 
movie_genres_df.registerTempTable("movie_genres")

#filter movies after 1995
query = "SELECT name, year, rating FROM movies INNER JOIN movie_genres ON movies.movie_id = movie_genres.movie_id WHERE movies.year > 1995 and movies.rating <> 0 and movie_genres.genre == 'Comedy'"
join_data = sc.sql(query)
join_data.registerTempTable("join_data")


query = "SELECT * FROM join_data WHERE rating IN (SELECT MAX(rating) FROM join_data GROUP BY year) ORDER BY year"
sort_movies = sc.sql(query)
sort_movies.show(30, False)

# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q4: ')
    fd.write(str(time_avg))
    fd.write('\n')