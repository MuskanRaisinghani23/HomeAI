from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("MySparkJob") \
    .getOrCreate()

# Your Spark code here
data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
df = spark.createDataFrame(data, ["name", "value"])

# df.write.csv("output.csv", header=True, mode="overwrite")

# Perform some Spark operations
df.show()

# Stop the Spark session
spark.stop()
