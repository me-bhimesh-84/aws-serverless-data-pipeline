import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

glue = boto3.client("glue")

CRAWLER_NAME = os.environ["CRAWLER_NAME"]

def lambda_handler(event, context):

    logger.info("========== NEW VERSION ==========")
    logger.info(f"Using crawler: {CRAWLER_NAME}")

    try:
        glue.start_crawler(Name=CRAWLER_NAME)

        logger.info("Crawler started successfully.")

        return {
            "statusCode": 200,
            "body": "Crawler started."
        }

    except glue.exceptions.CrawlerRunningException:
        logger.info("Crawler already running.")
        return {
            "statusCode": 200,
            "body": "Crawler already running."
        }

    except Exception as e:
        logger.exception(e)
        raise