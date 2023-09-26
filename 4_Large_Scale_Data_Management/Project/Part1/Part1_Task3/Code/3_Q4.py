from pyspark.sql import SparkSession
from pyspark.sql.functions import col, max
from pyspark.sql.window import Window

# Q1: Find and print the most popular Comedy movies for every year after 1995

sc = SparkSession \
    .builder \
    .appName("Dataframe query 4 execution") \
    .getOrCreate()

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
movie_genres_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movie_genres.parquet')

#filter movies after 1995
movies_filtered = movies_df.filter(movies_df.year > 1995)

#filter movies genre 
movie_genres_filtered = movie_genres_df.filter(movie_genres_df.genre == 'Comedy')

join_data = movies_filtered.join(movie_genres_filtered, movies_filtered.movie_id == movie_genres_filtered.movie_id, "inner")

#print results
sort_movies = join_data.withColumn('max_rating', max('rating').over(Window.partitionBy('year'))).where(col('rating') == col('max_rating')).orderBy("year")
sort_movies.select("year","name","rating").show(30, False)
