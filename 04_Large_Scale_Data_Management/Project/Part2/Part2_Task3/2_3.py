from pyspark.sql import SparkSession
import time
import sys

sc = SparkSession \
    .builder \
    .appName('query1-sql') \
    .getOrCreate()

disabled = sys.argv[1]

if disabled == "Y":
    sc.conf.set("spark.sql.autoBroadcastJoinThreshold",-1)
elif disabled == 'N':
    pass
else:
    raise Exception ("This setting is not available.")


# read files
dep_df = sc.read.parquet("hdfs://master:9000/home/user/project/parquet/departmentsR.parquet")
empl_df = sc.read.parquet("hdfs://master:9000/home/user/project/parquet/employeesR.parquet")

# Load temp table
dep_df.registerTempTable("departmentsR")
empl_df.registerTempTable("employeesR")



# query
query = "SELECT * FROM departmentsR d, employeesR e WHERE d.dep_id=e.dep_id"
sql_query=sc.sql(query)



t1 = time.time()
sql_query.show()
t2 = time.time()
sql_query.explain()



print("Time with choosing join type %s is %.4f sec."%("enabled" if
disabled == 'N' else "disabled", t2-t1))