#!/bin/bash

# DynamoDB Local単体起動スクリプト

echo "🚀 DynamoDB Local を起動します..."

# DynamoDB Local をDockerで起動
docker run -d \
  --name dynamodb-local \
  -p 8000:8000 \
  amazon/dynamodb-local:latest \
  -jar DynamoDBLocal.jar \
  -sharedDb \
  -inMemory

echo "⏳ DynamoDB Local起動を待機中..."
sleep 3

# DynamoDB Localの動作確認
echo "🔍 DynamoDB Local ヘルスチェック..."
curl -s http://localhost:8000 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ DynamoDB Local が正常に起動しました (localhost:8000)"
else
    echo "❌ DynamoDB Local の起動に失敗しました"
    exit 1
fi

# テーブル作成
echo "📋 todos テーブルを作成中..."
aws dynamodb create-table \
    --table-name todos \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=todo_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=todo_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000 \
    --region us-east-1

echo "✅ DynamoDB Local セットアップ完了！"
echo "🔗 DynamoDB Local URL: http://localhost:8000"
echo "📋 使用可能なテーブル:"
aws dynamodb list-tables --endpoint-url http://localhost:8000 --region us-east-1