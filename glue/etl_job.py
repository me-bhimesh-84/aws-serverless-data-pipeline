import sys
import logging

from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.context import SparkContext
from pyspark.sql.functions import col

# Logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Configuration
RAW_PATH = "s3://bhime-data-pipeline-raw/"
PROCESSED_PATH = "s3://bhime-data-pipeline-processed/clean-data/"

# ETL

try:

    logger.info("Reading raw CSV files...")

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(RAW_PATH)
    )

    before = df.count()
    logger.info(f"Rows before cleaning: {before}")

    # Remove duplicates
    df = df.dropDuplicates()

    # Remove rows with NULL values
    df = df.na.drop()

    after = df.count()
    logger.info(f"Rows after cleaning: {after}")

    removed = before - after
    logger.info(f"Rows removed: {removed}")

    logger.info("Writing Snappy-compressed Parquet...")

    (
        df.coalesce(1)
          .write
          .mode("overwrite")
          .option("compression", "snappy")
          .parquet(PROCESSED_PATH)
    )

    logger.info("ETL completed successfully.")

except Exception as e:
    logger.exception("Glue ETL failed.")
    raise e

finally:
    job.commit()