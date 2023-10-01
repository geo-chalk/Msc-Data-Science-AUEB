from pyspark.sql import SparkSession

#Q5: For every year print the average movie revenue 

sc = SparkSession \
    .builder \
    .appName("Dataframe query 5 execution") \
    .getOrCreate() 

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')

#find average revenue per year
movie_revenue = movies_df.filter((movies_df.year > 0) & (movies_df.revenue > 0))

#print results 
movie_revenue.groupBy("year").avg("revenue").sort("year").show(250)
