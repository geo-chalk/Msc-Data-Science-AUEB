from pyspark.sql import SparkSession

sc = SparkSession \
    .builder \
    .appName("broadcast") \
    .getOrCreate() \
    .sparkContext

# read data
departments = sc.textFile("hdfs://master:9000/home/user/project/csv/departmentsR.csv") \
            .map(lambda x: (x.split(",")))

employees = sc.textFile("hdfs://master:9000/home/user/project/csv/employeesR.csv") \
            .map(lambda x: (x.split(","))) 

# map <k,v>
departments_formatted = departments.map(lambda x: [x[0], [x[1]]])

# count the number of classes
num_of_partitions = len(departments.map(lambda x: x[0]).countByKey())

# map <k,v>
employees_formatted = employees.map(lambda x: [x[2], [x[0], x[1]]])

# broadcast join
joined_data = departments_formatted.leftOuterJoin(employees_formatted, num_of_partitions)

print('dep_id,dep_name, employee_id, employee_name')
for i in joined_data.collect():
    print(','.join([i[0], i[1][0][0], i[1][1][0], i[1][1][1]]))

