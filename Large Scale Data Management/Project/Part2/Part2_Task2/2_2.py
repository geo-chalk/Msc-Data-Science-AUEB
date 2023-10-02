from pyspark.sql import SparkSession

def arrange(seq):
    """Function to return the values with the tag '1' on the right and the ones with tag '2' on the left.
    """
    left_origin = []
    right_origin = []
    for (n, v) in seq:
        if n == '1':
            left_origin.append(v)
        elif n == '2':
            right_origin.append(v)
    return [(v, w) for v in left_origin for w in right_origin]

sc = SparkSession \
    .builder \
    .appName("repartition") \
    .getOrCreate() \
    .sparkContext


# read data
departments = sc.textFile("hdfs://master:9000/home/user/project/csv/departmentsR.csv") \
            .map(lambda x: (x.split(",")))

employees = sc.textFile("hdfs://master:9000/home/user/project/csv/employeesR.csv") \
            .map(lambda x: (x.split(","))) 

# Map and tag
left = departments.map(lambda x: [x[0], [x[1]]]) \
        .map(lambda x: [x[0],["1",x[1]]])

right = employees.map(lambda x: [x[2] ,[x[0], x[1]]]) \
        .map(lambda x: [x[0],["2",x[1]]])

# join the data
unioned_data = left.union(right)

grouped_join=unioned_data.groupByKey().mapValues(list)

# map the output with formatting
output = grouped_join.flatMapValues(lambda x: arrange(x))\
    .map(lambda x: [x[0], x[1][0][0],  x[1][1][0], x[1][1][1]])


print('dep_id,dep_name, employee_id, employee_name')
for i in output.collect():
    print(','.join(i))