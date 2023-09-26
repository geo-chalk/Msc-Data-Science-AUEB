from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, StringType, TimestampType


def convert():  
    # define the schemas
    department_schema = StructType([
            StructField("dep_id", IntegerType(), True),
            StructField("dep_name", StringType(), True)])

    employees_schema = StructType([
            StructField("emp_id", IntegerType(), True),
            StructField("emp_name", StringType(), True),
            StructField("dep_id", StringType(), True)
            ])

    movie_genres_schema = StructType([
            StructField("movie_id", IntegerType(), True),
            StructField("genre", StringType(), True)
            ])

    movies_schema = StructType([
            StructField("movie_id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("year", StringType(), True),
            StructField("duration", IntegerType(), True),
            StructField("cost", IntegerType(), True),
            StructField("revenue", IntegerType(), True),
            StructField("rating", DoubleType(), True)
            ])

    ratings_schema = StructType([
            StructField("user_id", IntegerType(), True),
            StructField("movie_id", IntegerType(), True),
            StructField("rating", DoubleType(), True),
            StructField("timestamp", StringType(), True)
            ])

    # Create schema dict
    schema_map = {'departmentsR': department_schema,
            'employeesR':employees_schema,
            'movies' : movies_schema,
            'ratings' : ratings_schema,
            'movie_genres' : movie_genres_schema
            }

    # Iterate files needed for conversion
    for file in ['departmentsR', 'employeesR', 'movies', 'ratings', 'movie_genres']:

        # Create sparksession
        sc = SparkSession \
            .builder \
            .appName("CSV to Parquet") \
            .getOrCreate()

        # load the file
        path_csv = ''.join(["hdfs://master:9000/home/user/project/csv/",file,".csv"])
        df = sc.read.csv(path_csv,header=False, schema= schema_map[file])

        # write to parquet
        path_parquet = ''.join(["hdfs://master:9000/home/user/project/parquet/",file,".parquet"])
        df.repartition(1).write.mode('overwrite').parquet(path_parquet)

        # read and show
        df = sc.read.parquet(path_parquet)
        print(df.show(3))

if __name__ == "__main__":
    convert()
