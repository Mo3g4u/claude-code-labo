# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

日本語で出力してください。

## リポジトリ概要

`claude-code-labo`は claude code を利用した開発を行うための実験的なリポジトリです。Quasar Framework + Python Lambda + SAM + LocalStack + TDD構成でTodoアプリを実装します。

## 技術スタック

### フロントエンド
- **Quasar Framework** (Vue.js 3 + TypeScript)
- **Vitest** + **@testing-library/vue** (TDD)
- **Pinia** (状態管理)
- **Axios** (API通信)

### バックエンド
- **AWS Lambda** (Python 3.11)
- **API Gateway** + **DynamoDB**
- **AWS SAM** (Serverless Application Model)
- **pytest** + **moto** (TDD)

### ローカル開発環境
- **LocalStack** (AWS サービス模擬)
- **Docker Compose**

## 開発環境設定

### 前提条件
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- AWS CLI & SAM CLI
- Make

### セットアップ
```bash
# 開発環境初期化
make setup

# LocalStack + SAM Local 起動
make start

# 開発サーバー起動（フロントエンド）
make dev-frontend

# 開発サーバー起動（バックエンド）
make dev-backend
```

## 主要コマンド

### 開発
- `make setup` - 開発環境初期化
- `make start` - LocalStack + SAM Local 起動
- `make dev-frontend` - フロントエンド開発サーバー起動
- `make dev-backend` - バックエンド開発サーバー起動

### テスト (TDD)
- `make test` - 全テスト実行
- `make tdd-backend` - バックエンドTDD（watch mode）
- `make tdd-frontend` - フロントエンドTDD（watch mode）

### コード品質
- `make lint` - リンティング実行
- `make format` - コードフォーマット実行

### デプロイ
- `make build` - 本番ビルド
- `make deploy` - AWS デプロイ

## プロジェクト構造

```
├── frontend/           # Quasar アプリケーション
│   ├── src/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── services/
│   │   └── types/
│   └── tests/
├── backend/            # SAM + Python Lambda
│   ├── src/
│   │   ├── handlers/   # Lambda 関数
│   │   ├── models/     # Pydantic モデル
│   │   └── services/   # ビジネスロジック
│   └── tests/
├── api/
│   └── openapi.yaml    # OpenAPI 仕様書
├── docker-compose.yml  # LocalStack設定
└── Makefile           # 開発コマンド
```

## TDD開発プロセス（t-wada作法）

### 基本サイクル
1. **Red** - 失敗するテストを書く
2. **Green** - テストを通す最小限のコードを書く
3. **Refactor** - コードを改善する

### 実装順序
1. OpenAPI仕様書（テスト仕様として）
2. E2Eテスト作成（失敗する状態）
3. Lambda関数TDD実装
4. フロントエンドTDD実装
5.統合テスト + リファクタリング

## API仕様

Todo APIは以下のエンドポイントを提供します：
- `GET /todos` - Todo一覧取得
- `POST /todos` - Todo作成
- `GET /todos/{id}` - Todo詳細取得
- `PUT /todos/{id}` - Todo更新
- `DELETE /todos/{id}` - Todo削除

詳細は `api/openapi.yaml` を参照してください。