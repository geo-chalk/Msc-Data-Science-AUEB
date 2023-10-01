from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType, DoubleType
import time

# Q1: For every year after 1995 print the difference between the money spent to create the movie 
# and the revenue of the movie (revenue – production cost)?

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("Spark SQL CSV query 1 execution") \
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