from pyspark.sql import SparkSession
import time

# Q4: Find and print the most popular Comedy movies for every year after 1995

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark parquet query 4 execution") \
    .getOrCreate()

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
movie_genres_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movie_genres.parquet')
movies_df.registerTempTable("movies")
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