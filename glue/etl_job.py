from pyspark.sql import SparkSession
from pyspark.sql.functions import col

#Spark session creatoin
spark = SparkSession.builder.appName("RetailETL").getOrCreate()

#Read CSV from Raw Bucket
df = spark.read.option("header", "true").csv(
    "s3://bhime-data-pipeline-raw/"
)

print("Original Record Count:", df.count())

#duplicate rows removal
df = df.dropDuplicates()

#null values removal
df = df.na.drop()

print("Cleaned Record Count:", df.count())

# CSV to Parquet conversion
df.write \
    .mode("overwrite") \
    .parquet("s3://bhime-data-pipeline-processed/")

spark.stop()