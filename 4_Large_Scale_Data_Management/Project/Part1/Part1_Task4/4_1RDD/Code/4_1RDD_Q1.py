from pyspark.sql import SparkSession, SQLContext
import time

# Q1: For every year after 1995 print the difference between the money spent to create the movie 
# and the revenue of the movie (revenue – production cost)?


start = time.perf_counter()

sc = SparkSession \
       .builder \
       .appName("RDD query 1 execution") \
       .getOrCreate() \
       .sparkContext

movies = sc.textFile("hdfs://master:9000/home/user/project/csv/movies.csv") \
       .map(lambda x: (x.split(",")))

# filter out blank values
movies_filtered = movies.map(lambda x: x if x[3] != ' ' and x[5] != ' ' and x[6] != ' ' else None) \
       .filter(lambda x: x != None) 

# movies after 1995 with revenue and cost <> 0 
movies_filtered = movies_filtered.map(lambda x: x if (int(x[3]) > 1995) and float(x[5]) > 0 and float(x[6]) > 0 else None) \
       .filter(lambda x: x != None) 

# create list to print/save
movies_formatted = movies_filtered.map(lambda x: [x[1] , x[3], str(float(x[6]) - float(x[5]))] )

print('movie_id,year,rev_minus_cost')
for i in movies_formatted.collect():
    print(','.join(i))


# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q1: ')
    fd.write(str(time_avg))
    fd.write('\n')