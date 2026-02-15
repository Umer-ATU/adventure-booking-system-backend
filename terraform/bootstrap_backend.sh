#!/bin/bash
set -e

# Creates an S3 bucket and DynamoDB table for Terraform state
PROJECT_NAME="helena"
REGION="eu-west-1"
BUCKET_NAME="${PROJECT_NAME}-tfstate-$(openssl rand -hex 6)"
TABLE_NAME="${PROJECT_NAME}-tfstate-lock"

echo "Using region: $REGION"
echo "Creating Terraform state bucket: $BUCKET_NAME"
aws s3api create-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION"

aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled

echo "Creating DynamoDB table for locking: $TABLE_NAME"
aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region "$REGION"

echo "Waiting for table to become active..."
aws dynamodb wait table-exists --table-name "$TABLE_NAME" --region "$REGION"

echo "Done! Add this to main.tf:"
echo ""
echo "backend \"s3\" {"
echo "  bucket         = \"$BUCKET_NAME\""
echo "  key            = \"terraform.tfstate\""
echo "  region         = \"$REGION\""
echo "  dynamodb_table = \"$TABLE_NAME\""
echo "  encrypt        = true"
echo "}"
