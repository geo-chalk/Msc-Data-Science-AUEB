from pyspark.sql import SparkSession, SQLContext
import time

# Q2: For the movie ”Cesare deve morire” find and print 
# the movies id and then search 
# how many users rated the movie and 
# what the average rating was?

time_avg = []
start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("RDD query 2 execution") \
    .getOrCreate() \
    .sparkContext

movies = sc.textFile("hdfs://master:9000/home/user/project/csv/movies.csv") \
            .map(lambda x: (x.split(",")))

# filter out other movies
movies_filtered = movies.map(lambda x: x if x[1] == 'Cesare deve morire' else None) \
    .filter(lambda x: x != None) 



# Create (k,v) pairs
movie_id = movies_filtered.take(1)[0][0]
movie_name = movies_filtered.take(1)[0][1]

ratings = sc.textFile("hdfs://master:9000/home/user/project/csv/ratings.csv") \
            .map(lambda x: (x.split(","))) \
            .map(lambda x: x if x[1] == movie_id else None) \
            .filter(lambda x: x != None) \
            .map(lambda x: float(x[2]))


# assign values to variables for printing
users = str(ratings.count())
mean_rating =  str(ratings.mean())


# print results
print('movie_id,movie_name,num_of_users,mean_rating')
print(','.join([movie_id, movie_name, users, mean_rating]))


# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q2: ')
    fd.write(str(time_avg))
    fd.write('\n')
