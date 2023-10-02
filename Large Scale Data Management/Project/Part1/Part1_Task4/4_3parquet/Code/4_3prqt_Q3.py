from pyspark.sql import SparkSession
import time

#Q3: What was the best in term of revenue Animation movie of 1995?

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark parquet query 3 execution") \
    .getOrCreate() 

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
movie_genres_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movie_genres.parquet')

movies_df.registerTempTable("movies")
movie_genres_df.registerTempTable("movie_genres")

#find best in term of revenue Animation movie of 1995
query = "SELECT movies.name FROM movies INNER JOIN movie_genres ON movies.movie_id = movie_genres.movie_id WHERE movie_genres.genre = 'Animation' and movies.year = 1995 and movies.revenue > 0 ORDER BY movies.revenue DESC"
movie = sc.sql(query)

print("The best in term of revenue Animation movie of 1995 was",movie.collect()[0][0])

# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q3: ')
    fd.write(str(time_avg))
    fd.write('\n')