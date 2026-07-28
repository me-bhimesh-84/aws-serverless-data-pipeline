import json
import boto3
import os
import logging
from datetime import datetime
from botocore.exceptions import ClientError

#logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3") 


RAW_BUCKET = os.environ["RAW_BUCKET"] #environment variable


def lambda_handler(event, context):

    try:
        #exatract s3 event info
        record = event["Records"][0]

        source_bucket = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

        logger.info(f"Source Bucket : {source_bucket}")
        logger.info(f"Uploaded File : {object_key}")

        
        allowed_extensions = (".csv", ".parquet") #it validates the files uploaded in the bucket

        if not object_key.lower().endswith(allowed_extensions):

            logger.warning(
                f"Rejected file '{object_key}'. Unsupported file type."
            )

            return {
                "statusCode": 400,
                "body": json.dumps(
                    "Only CSV and Parquet files are supported."
                )
            }

        
        filename = os.path.basename(object_key) # creates the timestamped filename

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        destination_key = f"{timestamp}_{filename}"

        # copy the original file to raw bucket with timestamp
        copy_source = {
            "Bucket": source_bucket,
            "Key": object_key
        }

        s3.copy_object(
            Bucket=RAW_BUCKET,
            CopySource=copy_source,
            Key=destination_key
        )

        logger.info("File copied successfully.")

        logger.info(
            {
                "status": "SUCCESS",
                "source_bucket": source_bucket,
                "destination_bucket": RAW_BUCKET,
                "source_file": object_key,
                "destination_file": destination_key
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "File copied successfully.",
                    "destination_file": destination_key
                }
            )
        }

    except ClientError as error:

        logger.exception("AWS Client Error")

        return {
            "statusCode": 500,
            "body": json.dumps(str(error))
        }

    except Exception as error:

        logger.exception("Unexpected Error")

        return {
            "statusCode": 500,
            "body": json.dumps(str(error))
        }