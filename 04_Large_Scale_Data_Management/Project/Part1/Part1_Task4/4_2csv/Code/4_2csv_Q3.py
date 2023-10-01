from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, DoubleType
import time

#Q3: What was the best in term of revenue Animation movie of 1995?

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark CSV query 3 execution") \
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