from pyspark.sql import SparkSession

# Q1: For every year after 1995 print the difference between the money spent to create the movie 
# and the revenue of the movie (revenue – production cost)?

sc = SparkSession \
    .builder \
    .appName("Dataframe query 1 execution") \
    .getOrCreate()

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')

# movies after 1995 with revenue and cost <> 0 
movies_filtered = movies_df.filter((movies_df.year > 1995) & (movies_df.cost > 0) & (movies_df.revenue > 0))

#calculate revenue - cost
movies_formatted = movies_filtered.withColumn('profit', (movies_filtered["revenue"] - movies_filtered["cost"]))

# print results
movies_formatted = movies_formatted.select("name","year","profit")
movies_formatted.show(4000, False)