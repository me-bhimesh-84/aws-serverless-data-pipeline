import json
import os
import logging
from datetime import datetime

import boto3

# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ------------------------------------------------------------------
# AWS Clients
# ------------------------------------------------------------------

s3 = boto3.client("s3")
glue = boto3.client("glue")

# ------------------------------------------------------------------
# Environment Variables
# ------------------------------------------------------------------

RAW_BUCKET = os.environ["RAW_BUCKET"]
GLUE_JOB_NAME = os.environ["GLUE_JOB_NAME"]

# ------------------------------------------------------------------
# Lambda Handler
# ------------------------------------------------------------------

def lambda_handler(event, context):

    try:

        # Read S3 Event
        record = event["Records"][0]
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = record["s3"]["object"]["key"]

        logger.info(f"New file detected: {source_key}")

        # ----------------------------------------------------------
        # Validate File Type
        # ----------------------------------------------------------

        if not source_key.lower().endswith((".csv", ".parquet")):
            logger.warning("Unsupported file type. Skipping processing.")

            return {
                "statusCode": 400,
                "body": "Unsupported file type."
            }

        # ----------------------------------------------------------
        # Generate Timestamped Filename
        # ----------------------------------------------------------

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        filename = source_key.split("/")[-1]

        destination_key = f"{timestamp}_{filename}"

        # ----------------------------------------------------------
        # Copy File to Raw Bucket
        # ----------------------------------------------------------

        logger.info(f"Copying file to {RAW_BUCKET}")

        s3.copy_object(
            Bucket=RAW_BUCKET,
            CopySource={
                "Bucket": source_bucket,
                "Key": source_key
            },
            Key=destination_key
        )

        logger.info("File copied successfully.")

        # ----------------------------------------------------------
        # Start Glue Job
        # ----------------------------------------------------------

        response = glue.start_job_run(
            JobName=GLUE_JOB_NAME
        )

        logger.info(
            f"Glue Job Started Successfully. JobRunId: {response['JobRunId']}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File copied and Glue job triggered successfully.",
                "jobRunId": response["JobRunId"]
            })
        }

    except Exception as e:

        logger.exception("Pipeline execution failed.")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }