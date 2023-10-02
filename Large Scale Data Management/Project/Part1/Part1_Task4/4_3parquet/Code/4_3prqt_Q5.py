from pyspark.sql import SparkSession
import time

#Q5: For every year print the average movie revenue 

start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("SQL Spark query 5 execution") \
    .getOrCreate() 

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
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