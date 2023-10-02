from pyspark.sql import SparkSession, SQLContext
import time

# Q4: What was the best in term of revenue Animation movie of 1995?

time_avg = []
start = time.perf_counter()

sc = SparkSession \
    .builder \
    .appName("RDD query 4 execution") \
    .getOrCreate() \
    .sparkContext


# read data
movies = sc.textFile("hdfs://master:9000/home/user/project/csv/movies.csv") \
       .map(lambda x: (x.split(",")))

genre = sc.textFile("hdfs://master:9000/home/user/project/csv/movie_genres.csv") \
       .map(lambda x: (x.split(","))) 


# filters
movies_filtered = movies.map(lambda x: x if x[3] != ' ' and x[7] != ' 'else None) \
       .filter(lambda x: x != None) 

genre_filtered = genre.map(lambda x: x if x[1] == 'Comedy' else None) \
       .filter(lambda x: x != None) 

# movies after 1995 with revenue and cost <> 0 
movies_filtered = movies_filtered.map(lambda x: x if (int(x[3]) > 1995) else None) \
       .filter(lambda x: x != None) 

movies_formatted = movies_filtered.map(lambda x: [x[0], [x[3], x[1], x[7]]])

genre_formatted = genre_filtered.map(lambda x: [x[0], [x[1]]])


joined_data = movies_formatted.join(genre_formatted)


get_movies = joined_data.map(lambda x: (x[1][0]))
get_movies = get_movies.map(lambda x: [x[0], [x[1], x[2]]])

# print(get_movies.take(3))


get_movies = get_movies.groupByKey().mapValues(list) 
# print(get_movies.take(3))

sort_movies = get_movies.map(lambda x: [x[0], sorted(x[1], key=lambda tup: float(tup[1]), reverse=True)])\
       .map(lambda x: (x[0], x[1][0]))
sort_movies = sort_movies.sortByKey(ascending=True)

print('year,movie,rating')
for i in sort_movies.collect():
    print(','.join([i[0], i[1][0], i[1][1]]))


# Time
time_avg = time.perf_counter() - start
with open('time.txt', 'a') as fd:
    fd.write('Q4: ')
    fd.write(str(time_avg))
    fd.write('\n')

