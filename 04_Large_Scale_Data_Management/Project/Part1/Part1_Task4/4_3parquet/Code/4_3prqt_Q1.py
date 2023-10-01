from pyspark.sql import SparkSession
import time

# Q1: For every year after 1995 print the difference between the money spent to create the movie 
# and the revenue of the movie (revenue – production cost)?

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("Spark SQL parquet query 1 execution") \
    .getOrCreate()

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
movies_df.registerTempTable("movies")

# movies after 1995 with revenue and cost <> 0 
query = "SELECT movies.name, movies.year, SUM(movies.revenue - movies.cost) FROM movies WHERE movies.year > 1995 AND movies.cost > 0 AND movies.revenue > 0 GROUP BY movies.name, movies.year"
movies_filtered = sc.sql(query)
movies_filtered.show(4000, False)

# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q1: ')
    fd.write(str(time_avg))
    fd.write('\n')