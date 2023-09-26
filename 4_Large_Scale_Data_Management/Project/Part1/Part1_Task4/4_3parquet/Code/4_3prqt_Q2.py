from pyspark.sql import SparkSession
import time

# Q2: For the movie Cesare deve morire find and print 
# the movies id and then search 
# how many users rated the movie and 
# what the average rating was?

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark parquet query 2 execution") \
    .getOrCreate()

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
ratings_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/ratings.parquet')

movies_df.registerTempTable("movies")
ratings_df.registerTempTable("ratings")

#find movie_id of "Cesare deve morire"
query = "SELECT movies.movie_id FROM movies WHERE movies.name == 'Cesare deve morire'"
movie_id = sc.sql(query).collect()

#find movie_id of "Cesare deve morire"
query = "SELECT ratings.movie_id, COUNT(ratings.user_id) AS users, AVG(ratings.rating) AS average_rating FROM ratings WHERE ratings.movie_id == {} group by ratings.movie_id".format(movie_id[0].movie_id)
movie = sc.sql(query).collect()

print("The movie ID of 'Cesare deve morire' is:", movie_id[0].movie_id)
print("The 'Cesare deve morire' movie was rated by", movie[0].users, "users and has an average rating of", movie[0].average_rating)

# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q2: ')
    fd.write(str(time_avg))
    fd.write('\n')