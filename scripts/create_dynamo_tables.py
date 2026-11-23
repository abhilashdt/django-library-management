"""
One-time DynamoDB table bootstrap script.

Run this ONCE before deploying to AWS to create the three tables the app needs:
    python scripts/create_dynamo_tables.py

Environment variables read:
    AWS_REGION              (default: us-east-1)
    AWS_ACCESS_KEY_ID       – or use an IAM role / ~/.aws profile
    AWS_SECRET_ACCESS_KEY
    DYNAMODB_ENDPOINT_URL   – set to http://localhost:8000 for local DynamoDB
    DYNAMO_BOOKS_TABLE      (default: library_books)
    DYNAMO_MEMBERS_TABLE    (default: library_members)
    DYNAMO_LOANS_TABLE      (default: library_loans)

The script is idempotent: it skips tables that already exist.
"""

import os
import sys

import boto3
from botocore.exceptions import ClientError

AWS_REGION        = os.environ.get("AWS_REGION", "us-east-1")
ENDPOINT          = os.environ.get("DYNAMODB_ENDPOINT_URL")
BOOKS_TABLE       = os.environ.get("DYNAMO_BOOKS_TABLE",   "library_books")
MEMBERS_TABLE     = os.environ.get("DYNAMO_MEMBERS_TABLE", "library_members")
LOANS_TABLE       = os.environ.get("DYNAMO_LOANS_TABLE",   "library_loans")

kwargs = dict(region_name=AWS_REGION)
if ENDPOINT:
    kwargs["endpoint_url"] = ENDPOINT

dynamodb = boto3.client("dynamodb", **kwargs)


def create_table_if_not_exists(params: dict):
    name = params["TableName"]
    try:
        dynamodb.create_table(**params)
        print(f"  Created table: {name}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceInUseException":
            print(f"  Table already exists (skipped): {name}")
        else:
            raise
    # Wait until the table becomes ACTIVE
    waiter = dynamodb.get_waiter("table_exists")
    waiter.wait(TableName=name)
    print(f"  Table ACTIVE: {name}")


def main():
    print("=== DynamoDB Table Bootstrap ===")

    # ── library_books ──────────────────────────────────────────────────────────
    create_table_if_not_exists({
        "TableName": BOOKS_TABLE,
        "BillingMode": "PAY_PER_REQUEST",   # on-demand – no capacity planning
        "AttributeDefinitions": [
            {"AttributeName": "book_id", "AttributeType": "S"},
            {"AttributeName": "isbn",    "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "book_id", "KeyType": "HASH"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "isbn-index",
                "KeySchema": [{"AttributeName": "isbn", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "KEYS_ONLY"},
            }
        ],
    })

    # ── library_members ────────────────────────────────────────────────────────
    create_table_if_not_exists({
        "TableName": MEMBERS_TABLE,
        "BillingMode": "PAY_PER_REQUEST",
        "AttributeDefinitions": [
            {"AttributeName": "member_id", "AttributeType": "S"},
            {"AttributeName": "email",     "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "member_id", "KeyType": "HASH"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "email-index",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "KEYS_ONLY"},
            }
        ],
    })

    # ── library_loans ──────────────────────────────────────────────────────────
    create_table_if_not_exists({
        "TableName": LOANS_TABLE,
        "BillingMode": "PAY_PER_REQUEST",
        "AttributeDefinitions": [
            {"AttributeName": "loan_id", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "loan_id", "KeyType": "HASH"},
        ],
    })

    print("\nAll tables are ready. You can now deploy the application.")


if __name__ == "__main__":
    main()
