#!/bin/bash

# LocalStack初期化スクリプト
# DynamoDBテーブルの作成

echo "Initializing LocalStack resources..."

# DynamoDBテーブル作成
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
    --table-name todos \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=todo_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=todo_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1

# テーブル作成確認
aws --endpoint-url=http://localhost:4566 dynamodb describe-table \
    --table-name todos \
    --region us-east-1

echo "LocalStack initialization completed!"