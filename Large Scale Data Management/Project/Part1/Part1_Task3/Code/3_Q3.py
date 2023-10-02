from pyspark.sql import SparkSession

#Q3: What was the best in term of revenue Animation movie of 1995?

sc = SparkSession \
    .builder \
    .appName("Dataframe query 3 execution") \
    .getOrCreate() 

movies_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movies.parquet')
movie_genres_df = sc.read.parquet('hdfs://master:9000/home/user/project/parquet/movie_genres.parquet')

#find best in term of revenue Animation movie of 1995
movies_filtered = movies_df.filter(((movies_df.year == 1995) & (movies_df.revenue > 0)))
movie_genres_filtered = movie_genres_df.filter(movie_genres_df.genre == 'Animation')
movie = movies_filtered.join(movie_genres_filtered, movies_filtered.movie_id == movie_genres_filtered.movie_id, "inner")

#ptint the movie with the most revenue in 1995
sorted_movie = movie.sort(movie.revenue.desc()).collect()[0]
best_movie = sorted_movie[1]
revenue = sorted_movie[6]
print("The best in term of revenue Animation movie of 1995 was",best_movie,"with a revenue of", revenue)

