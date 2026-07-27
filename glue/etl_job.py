import sys

from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.context import SparkContext
from pyspark.sql.functions import col


# Glue Boilerplate

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()

glueContext = GlueContext(sc)

spark = glueContext.spark_session

job = Job(glueContext)

job.init(args['JOB_NAME'], args)

# Configuration

RAW_PATH = "s3://bhime-data-pipeline-raw/"

PROCESSED_PATH = "s3://bhime-data-pipeline-processed/"

# Read Raw CSV

print("Reading data...")

df = spark.read \
    .option("header", True) \
    .option("inferSchema", True) \
    .csv(RAW_PATH)

print(f"Rows Before Cleaning : {df.count()}")

# Remove Duplicate Records

df = df.dropDuplicates()

# Remove Null Values

df = df.na.drop()

print(f"Rows After Cleaning : {df.count()}")

# Convert CSV → Parquet

df.write \
    .mode("overwrite") \
    .parquet(PROCESSED_PATH)

print("Parquet files written successfully.")

job.commit()