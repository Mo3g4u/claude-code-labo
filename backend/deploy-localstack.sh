#!/bin/bash

# LocalStack完全版デプロイスクリプト

echo "🚀 LocalStackに完全なAWSスタックをデプロイします..."

# 1. S3バケット作成（SAMデプロイに必要）
echo "📦 S3バケット作成..."
awslocal s3 mb s3://sam-deployment-bucket --endpoint-url=http://localhost:4566

# 2. SAMビルド
echo "🔨 SAMビルド実行..."
sam build

# 3. LocalStackにデプロイ
echo "🚀 LocalStackデプロイ実行..."
sam deploy \
  --stack-name todo-app-local \
  --s3-bucket sam-deployment-bucket \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --endpoint-url http://localhost:4566 \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

echo "✅ LocalStackデプロイ完了！"

# 4. API Gateway URLを取得
echo "🔗 API Gateway URL取得..."
API_ID=$(awslocal apigateway get-rest-apis --endpoint-url=http://localhost:4566 --query 'items[0].id' --output text)

if [ "$API_ID" != "None" ]; then
    echo "📡 API Gateway URL: http://localhost:4566/restapis/$API_ID/local/_user_request_/"
    echo "📋 テスト用URL:"
    echo "   GET  http://localhost:4566/restapis/$API_ID/local/_user_request_/todos?user_id=user123"
    echo "   POST http://localhost:4566/restapis/$API_ID/local/_user_request_/todos"
else
    echo "⚠️  API Gateway URLの取得に失敗しました"
fi

# 5. デプロイされたリソースを確認
echo "🔍 デプロイされたリソース:"
echo "DynamoDB Tables:"
awslocal dynamodb list-tables --endpoint-url=http://localhost:4566

echo "Lambda Functions:"
awslocal lambda list-functions --endpoint-url=http://localhost:4566 --query 'Functions[].FunctionName'

echo "API Gateways:"
awslocal apigateway get-rest-apis --endpoint-url=http://localhost:4566 --query 'items[].name'