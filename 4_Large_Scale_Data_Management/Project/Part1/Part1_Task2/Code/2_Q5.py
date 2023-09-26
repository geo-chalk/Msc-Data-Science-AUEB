from pyspark.sql import SparkSession, SQLContext

# Q5: For every year print the average movie revenue 

sc = SparkSession \
    .builder \
    .appName("RDD query 4 execution") \
    .getOrCreate() \
    .sparkContext

# read data
movies = sc.textFile("hdfs://master:9000/home/user/project/csv/movies.csv") \
            .map(lambda x: (x.split(",")))

# filter out blank values
movies_filtered = movies.map(lambda x: x if x[3] != ' ' and x[6] != ' ' else None) \
       .filter(lambda x: x != None) 

# movies after 1995 with revenue and cost <> 0 
movies_filtered = movies_filtered.map(lambda x: x if (int(x[3]) > 0) and float(x[6]) > 0 else None) \
       .filter(lambda x: x != None) 

# filters
get_movies = movies_filtered.map(lambda x: [int(x[3]), int(x[6])])


def avg_map_func(row):
    return (int(row[0]), (int(row[1]), 1))

def avg_reduce_func(value1, value2):
    return ((value1[0] + value2[0], value1[1] + value2[1])) 

reduced = get_movies.map(avg_map_func).reduceByKey(avg_reduce_func).mapValues(lambda x: int(x[0]/x[1]))
top = reduced.sortByKey(ascending=True).collect()

print('year,avg_revenue')
for i in top:
    print(','.join([str(i[0]), str(i[1])]))

