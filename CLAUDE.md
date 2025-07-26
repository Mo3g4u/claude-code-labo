# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

日本語で出力してください。

## リポジトリ概要

`claude-code-labo`は Claude Code を利用した開発を行うための実験的なリポジトリです。Quasar Framework + Python Lambda + SAM + AWS Cognito + LocalStack + TDD構成でユーザー認証機能付きTodoアプリを実装し、完全なCI/CDパイプラインを含む現代的な開発環境を構築しています。

## 技術スタック

### フロントエンド
- **Quasar Framework** (Vue.js 3 + TypeScript)
- **Vitest** + **Vue Test Utils** (TDD)
- **Axios** (API通信)
- **ESLint** + **TypeScript** (コード品質)

### バックエンド
- **AWS Lambda** (Python 3.11)
- **API Gateway** + **DynamoDB**
- **AWS SAM** (Serverless Application Model)
- **pytest** + **moto** (TDD)
- **ruff** + **mypy** (コード品質・型チェック)

### 認証・セキュリティ
- **AWS Cognito** (ユーザー認証・認可)
- **JWT トークン** (API アクセス制御)
- **amazon-cognito-identity-js** (フロントエンド認証SDK)

### ローカル開発環境
- **LocalStack** (DynamoDB + Cognito サービス模擬)
- **SAM Local** (API Gateway + Lambda ランタイム)
- **Docker Compose**

### CI/CD
- **GitHub Actions** (完全自動化)
- **開発フロー**: feature → develop PR → 自動テスト → マージ

## 開発環境設定

### 前提条件
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- AWS CLI & SAM CLI
- Make

### セットアップ
```bash
# LocalStack 起動（DynamoDB）
make localstack-up

# バックエンド起動（SAM Local）
make backend-start

# フロントエンド起動（Vite）
make frontend-start
```

## 主要コマンド

### 開発サーバー
- `make localstack-up` - LocalStack（DynamoDB）起動
- `make backend-start` - SAM Local（API Gateway + Lambda）起動
- `make frontend-start` - Vite開発サーバー起動

### テスト (TDD)
- `make test` - 全テスト実行
- `make backend-test` - バックエンドテスト（pytest）
- `make frontend-test` - フロントエンドテスト（Vitest）

### コード品質
- `make lint` - 全リンティング実行
- `make backend-lint` - ruff（Python）
- `make frontend-lint` - ESLint（JavaScript/Vue）

### ビルド
- `make build` - 全ビルド実行
- `make backend-build` - SAM ビルド
- `make frontend-build` - Vite ビルド

## プロジェクト構造

```
├── .github/workflows/
│   └── ci.yml              # GitHub Actions CI/CD
├── frontend/               # Quasar アプリケーション
│   ├── src/
│   │   ├── App.vue         # メインコンポーネント（認証状態管理）
│   │   ├── components/     # Vue コンポーネント
│   │   │   ├── AuthForm.vue       # 認証フォーム
│   │   │   ├── LoginForm.vue      # ログインフォーム
│   │   │   └── SignUpForm.vue     # サインアップフォーム
│   │   ├── services/       # API通信層・認証サービス
│   │   │   ├── authService.js     # Cognito認証サービス
│   │   │   └── todoApi.js         # Todo API（認証対応）
│   │   └── types/          # TypeScript型定義
│   ├── tests/
│   │   ├── unit/           # ユニットテスト
│   │   └── integration/    # 統合テスト
│   ├── .eslintrc.js        # ESLint設定
│   ├── tsconfig.json       # TypeScript設定
│   └── vitest.config.js    # Vitest設定
├── backend/                # SAM + Python Lambda + Cognito
│   ├── src/
│   │   ├── auth_helper.py  # JWT認証ヘルパー
│   │   └── handlers/       # Lambda 関数（認証対応）
│   │       ├── get_todos.py       # Todo一覧取得
│   │       ├── create_todo.py     # Todo作成
│   │       ├── get_todo.py        # Todo詳細取得
│   │       ├── update_todo.py     # Todo更新
│   │       └── delete_todo.py     # Todo削除
│   ├── tests/
│   │   ├── unit/           # ユニットテスト
│   │   └── integration/    # 統合テスト
│   ├── template.yaml       # SAM テンプレート（Cognito含む）
│   ├── pyproject.toml      # ruff/mypy設定
│   ├── env.json            # ローカル環境変数
│   ├── requirements.txt    # 本番依存関係（PyJWT追加）
│   └── requirements-dev.txt # 開発依存関係
├── api/
│   └── openapi.yaml        # OpenAPI 3.0 仕様書
├── architecture-comparison.md # アーキテクチャ比較
├── flow.md                 # システム動作フロー図
├── docker-compose.yml      # LocalStack設定
└── Makefile               # 開発コマンド
```

## ローカル開発環境アーキテクチャ

### Hybrid構成（推奨）
- **SAM Local** (localhost:3001): API Gateway + Lambda Runtime
- **LocalStack** (localhost:4566): DynamoDB のみ
- **Vite** (localhost:3000): フロントエンド開発サーバー
- **接続**: Lambda関数 → LocalStack DynamoDB

### 代替構成
1. **Pure SAM Local + DynamoDB Local**: 軽量・高速
2. **Complete LocalStack**: 本番前の完全AWS環境

詳細は `architecture-comparison.md` を参照してください。

## TDD開発プロセス（t-wada作法）

### 基本サイクル
1. **Red** - 失敗するテストを書く
2. **Green** - テストを通す最小限のコードを書く
3. **Refactor** - コードを改善する

### 実装順序
1. OpenAPI仕様書（テスト仕様として）
2. Lambda関数TDD実装（pytest + moto）
3. フロントエンドTDD実装（Vitest + Vue Test Utils）
4. 統合テスト + リファクタリング

## CI/CDパイプライン

### GitHub Actions ワークフロー
feature → develop PR時に自動実行：

1. **backend-tests**
   - DynamoDB Local 起動
   - ruff (リンティング + フォーマット)
   - mypy (型チェック)
   - pytest (テスト + カバレッジ)

2. **frontend-tests**
   - ESLint (リンティング)
   - Vitest (テスト + カバレッジ)

3. **build-validation**
   - Vite ビルド確認

### 品質ゲート
- 全テスト通過必須
- コードカバレッジ計測
- 型安全性保証
- コードスタイル統一

## 認証機能

### ユーザー認証フロー
1. **サインアップ**: メールアドレス・パスワード・名前でアカウント作成
2. **ログイン**: メールアドレス・パスワードで認証
3. **JWT トークン**: 認証成功後、API アクセス用のJWTトークンを取得
4. **自動ログイン**: ブラウザリロード時の認証状態復元
5. **ログアウト**: セッション終了とトークン無効化

### セキュリティ実装
- **Cognito User Pool**: AWS Cognitoによるユーザー管理
- **JWT 検証**: 全API エンドポイントでトークン検証
- **自動トークン付与**: axios インターセプターによる自動認証ヘッダー設定
- **401 エラーハンドリング**: トークン期限切れ時の自動ログアウト

### LocalStack 対応
- 開発環境では簡易認証（モック）を実装
- 本番環境では完全なCognito JWT検証を実行

## API仕様

Todo APIは以下のエンドポイントを提供します（全て認証必須）：
- `GET /todos` - Todo一覧取得（認証ユーザーのみ）
- `POST /todos` - Todo作成
- `GET /todos/{id}` - Todo詳細取得（所有者のみ）
- `PUT /todos/{id}` - Todo更新（所有者のみ）
- `DELETE /todos/{id}` - Todo削除（所有者のみ）

詳細は `api/openapi.yaml` を参照してください。

## 使用方法

### 初回セットアップ
```bash
# 依存関係インストール
make setup

# LocalStack起動
make localstack-up

# バックエンド起動（別ターミナル）
make backend-start

# フロントエンド起動（別ターミナル）
make frontend-start
```

### 認証フロー体験
1. ブラウザで `http://localhost:3000` にアクセス
2. 「新規登録」をクリックして新しいアカウントを作成
3. ログイン画面でメールアドレス・パスワードを入力してログイン
4. Todo の作成・編集・削除を試行
5. ログアウト後、再度ログインして Todo が復元されることを確認

### テスト用ユーザー（LocalStack）
LocalStack環境では以下のユーザーが自動的に作成されます：
- メール: `test@example.com`
- パスワード: `Password123`

## 動作確認

システム全体の動作フローとシーケンス図は `flow.md` で詳細に説明されています。

## 開発ガイドライン

### コードスタイル
- **Python**: ruff (現代的リンティング + フォーマット)
- **JavaScript/Vue**: ESLint + TypeScript
- **型注釈**: Python 3.11+ 形式（dict[str, Any]）

### テスト戦略
- **ユニットテスト**: 各関数・コンポーネント単位
- **統合テスト**: API疎通・E2E シナリオ
- **カバレッジ**: 80%以上を目標

### ブランチ戦略
- **develop**: デフォルトブランチ
- **feature/***: 機能開発ブランチ
- **PR**: feature → develop で自動CI実行

## トラブルシューティング

### よくある問題と解決方法

1. **DynamoDB接続エラー**
   ```bash
   # LocalStack再起動
   make localstack-down && make localstack-up
   ```

2. **npm依存関係エラー**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **SAM Local起動エラー**
   ```bash
   cd backend
   sam build
   make backend-start
   ```

## 参考資料

- [Quasar Framework](https://quasar.dev/)
- [AWS SAM](https://aws.amazon.com/serverless/sam/)
- [LocalStack](https://localstack.cloud/)
- [t-wada TDD作法](https://github.com/testdouble/contributing-tests/wiki/Test-Driven-Development)

---

**注意**: このプロジェクトは実験的な性質を持ちます。本番環境での使用前には十分な検証を行ってください。