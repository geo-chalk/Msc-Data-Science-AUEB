from pyspark.sql import SparkSession, SQLContext
import time

# Q3: What was the best in term of revenue Animation movie of 1995?

time_avg = []
start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("RDD query 3 execution") \
    .getOrCreate() \
    .sparkContext


# read data
movies = sc.textFile("hdfs://master:9000/home/user/project/csv/movies.csv") \
       .map(lambda x: (x.split(",")))

genre = sc.textFile("hdfs://master:9000/home/user/project/csv/movie_genres.csv") \
       .map(lambda x: (x.split(","))) 


# filters
movies_filtered = movies.map(lambda x: x if x[3] != ' ' and x[6] != ' 'else None) \
       .filter(lambda x: x != None) 

genre_filtered = genre.map(lambda x: x if x[1] == 'Animation' else None) \
       .filter(lambda x: x != None) 

# movies after 1995 with revenue and cost <> 0 
movies_filtered = movies_filtered.map(lambda x: x if (int(x[3]) == 1995) and float(x[6]) > 0 else None) \
       .filter(lambda x: x != None) 

movies_formatted = movies_filtered.map(lambda x: [x[0], [x[1], x[6]]])

genre_formatted = genre_filtered.map(lambda x: [x[0], [x[1]]])


joined_data = movies_formatted.join(genre_formatted)


get_movies = joined_data.map(lambda x: (int(x[1][0][1]), x[1][0][0]))

top = get_movies.sortByKey(ascending=False).take(1)[0]

print('movie,revenue')
print(','.join([top[1], str(top[0])]))


# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q3: ')
    fd.write(str(time_avg))
    fd.write('\n')