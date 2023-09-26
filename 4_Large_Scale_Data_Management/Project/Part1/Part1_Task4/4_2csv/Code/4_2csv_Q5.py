from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType,StringType, DoubleType, DecimalType
import time

#Q5: For every year print the average movie revenue 

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark CSV query 5 execution") \
    .getOrCreate() 

movie_schema = StructType([
         StructField("movie_id", IntegerType(), True),
         StructField("name", StringType(), True),
         StructField("description", StringType(), True),
         StructField("year", StringType(), True),
         StructField("duration", IntegerType(), True),
         StructField("cost", IntegerType(), True),
         StructField("revenue", DecimalType(20,0), True),
         StructField("rating", DoubleType(), True)])

movies_df = sc.read.format('csv').options(header='false').schema(movie_schema).load("hdfs://master:9000/home/user/project/csv/movies.csv") 
movies_df.registerTempTable("movies")

#find average revenue per year
query = "SELECT  movies.year, AVG(movies.revenue) FROM movies WHERE movies.year > 0 and movies.revenue > 0 GROUP BY movies.year ORDER BY movies.year"
revenue = sc.sql(query)
revenue.show(120, False)

# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q5: ')
    fd.write(str(time_avg))
    fd.write('\n')