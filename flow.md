# Todo アプリケーション動作フロー

## ローカル開発環境の構成

**重要**: ローカル環境では以下の分離された構成になっています：

- **SAM Local (localhost:3001)**: API Gateway + Lambda Runtime 
- **LocalStack (localhost:4566)**: DynamoDB のみ
- **接続**: Lambda関数が LocalStack の DynamoDB に接続

## システム全体構成図

```mermaid
graph TB
    subgraph "Frontend (localhost:3000)"
        UI[Vue.js + Quasar UI]
        ViteServer[Vite Dev Server]
    end
    
    subgraph "SAM Local (localhost:3001)"
        SAM[SAM Local API Gateway]
        Lambda1[Get Todos Function]
        Lambda2[Create Todo Function]
        Lambda3[Update Todo Function]
        Lambda4[Delete Todo Function]
        Lambda5[Get Todo Function]
    end
    
    subgraph "LocalStack (localhost:4566)"
        DynamoDB[(DynamoDB)]
        LocalStack[LocalStack Container]
    end
    
    subgraph "Development Environment"
        Docker[Docker Compose]
        TestSuite[Test Suite<br/>pytest + Vitest]
    end
    
    UI --> ViteServer
    ViteServer --> SAM
    SAM --> Lambda1
    SAM --> Lambda2
    SAM --> Lambda3
    SAM --> Lambda4
    SAM --> Lambda5
    Lambda1 --> DynamoDB
    Lambda2 --> DynamoDB
    Lambda3 --> DynamoDB
    Lambda4 --> DynamoDB
    Lambda5 --> DynamoDB
    Docker --> LocalStack
    LocalStack --> DynamoDB
```

## Todo作成フロー

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant UI as Vue.js UI
    participant API as todoApi Service
    participant Gateway as API Gateway
    participant Lambda as Create Todo Lambda
    participant DB as DynamoDB

    User->>UI: 新しいTodoを入力
    User->>UI: 「追加」ボタンをクリック
    
    UI->>UI: バリデーション実行
    alt バリデーションエラー
        UI->>User: エラーメッセージ表示
    else バリデーション成功
        UI->>API: createTodo(todoData)
        API->>Gateway: POST /todos
        Gateway->>Lambda: invoke create_todo.lambda_handler
        
        Lambda->>Lambda: リクエストボディ解析
        Lambda->>Lambda: UUID生成
        Lambda->>Lambda: タイムスタンプ生成
        
        Lambda->>DB: put_item(todo)
        DB-->>Lambda: 成功レスポンス
        Lambda-->>Gateway: HTTP 201 + todoデータ
        Gateway-->>API: レスポンス
        API-->>UI: 作成されたtodo
        
        UI->>API: getTodos() (リスト更新)
        API->>Gateway: GET /todos?user_id=user123
        Gateway->>Lambda: invoke get_todos.lambda_handler
        Lambda->>DB: query(user_id)
        DB-->>Lambda: todoリスト
        Lambda-->>Gateway: HTTP 200 + todos
        Gateway-->>API: todosリスト
        API-->>UI: 更新されたtodoリスト
        UI->>User: 新しいTodoを表示
    end
```

## Todo取得フロー

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant UI as Vue.js UI
    participant API as todoApi Service
    participant Gateway as API Gateway
    participant Lambda as Get Todos Lambda
    participant DB as DynamoDB

    User->>UI: ページを開く
    UI->>UI: mounted() ライフサイクル
    UI->>API: getTodos()
    
    API->>Gateway: GET /todos?user_id=user123
    Gateway->>Lambda: invoke get_todos.lambda_handler
    
    Lambda->>Lambda: user_id バリデーション
    alt user_id不足
        Lambda-->>Gateway: HTTP 400 Bad Request
        Gateway-->>API: エラーレスポンス
        API-->>UI: エラー
        UI->>User: エラーメッセージ表示
    else user_id正常
        Lambda->>DB: query(user_id=user123)
        DB-->>Lambda: todoアイテムリスト
        Lambda->>Lambda: DynamoDB形式→JSON変換
        Lambda-->>Gateway: HTTP 200 + {todos: [], count: n}
        Gateway-->>API: todosデータ
        API-->>UI: todoリスト
        UI->>User: Todoリストを表示
    end
```

## Todo更新フロー（完了切り替え）

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant UI as Vue.js UI
    participant API as todoApi Service
    participant Gateway as API Gateway
    participant Lambda as Update Todo Lambda
    participant DB as DynamoDB

    User->>UI: チェックボックスをクリック
    UI->>UI: toggleTodo(todo)
    UI->>UI: completed状態を反転
    
    UI->>API: updateTodo(todoId, updatedTodo)
    API->>Gateway: PUT /todos/{id}
    Gateway->>Lambda: invoke update_todo.lambda_handler
    
    Lambda->>Lambda: todo_id 取得
    Lambda->>Lambda: リクエストボディ解析
    
    Lambda->>DB: get_item(user_id, todo_id)
    alt Todo存在しない
        DB-->>Lambda: 空レスポンス
        Lambda-->>Gateway: HTTP 404 Not Found
        Gateway-->>API: エラー
        API-->>UI: エラー
        UI->>User: エラーメッセージ表示
    else Todo存在
        DB-->>Lambda: 既存todoデータ
        Lambda->>Lambda: 既存データ + 更新データをマージ
        Lambda->>Lambda: updated_at更新
        
        Lambda->>DB: put_item(updatedTodo)
        DB-->>Lambda: 成功レスポンス
        Lambda-->>Gateway: HTTP 200 + 更新されたtodo
        Gateway-->>API: 更新済みtodo
        API-->>UI: 更新済みtodo
        
        UI->>API: getTodos() (リスト更新)
        API-->>UI: 最新todoリスト
        UI->>User: 更新されたTodoを表示
    end
```

## Todo削除フロー

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant UI as Vue.js UI
    participant API as todoApi Service
    participant Gateway as API Gateway
    participant Lambda as Delete Todo Lambda
    participant DB as DynamoDB

    User->>UI: 削除ボタンをクリック
    UI->>UI: deleteTodo(todoId)
    
    UI->>API: deleteTodo(todoId)
    API->>Gateway: DELETE /todos/{id}?user_id=user123
    Gateway->>Lambda: invoke delete_todo.lambda_handler
    
    Lambda->>Lambda: todo_id取得
    Lambda->>Lambda: user_id取得
    
    Lambda->>DB: get_item(user_id, todo_id)
    alt Todo存在しない
        DB-->>Lambda: 空レスポンス
        Lambda-->>Gateway: HTTP 404 Not Found
        Gateway-->>API: エラー
        API-->>UI: エラー
        UI->>User: エラーメッセージ表示
    else Todo存在
        DB-->>Lambda: todoデータ
        Lambda->>DB: delete_item(user_id, todo_id)
        DB-->>Lambda: 削除成功
        Lambda-->>Gateway: HTTP 204 No Content
        Gateway-->>API: 削除成功
        API-->>UI: 削除成功
        
        UI->>API: getTodos() (リスト更新)
        API-->>UI: 更新されたtodoリスト
        UI->>User: Todoが削除された状態を表示
    end
```

## エラーハンドリングフロー

```mermaid
flowchart TD
    Start[リクエスト開始] --> Validate{入力バリデーション}
    
    Validate -->|失敗| ClientError[HTTP 400<br/>クライアントエラー]
    Validate -->|成功| DBCheck{DynamoDB接続}
    
    DBCheck -->|接続失敗| ServerError[HTTP 500<br/>サーバーエラー]
    DBCheck -->|成功| Operation{操作実行}
    
    Operation -->|データなし| NotFound[HTTP 404<br/>Not Found]
    Operation -->|成功| Success[HTTP 200/201/204<br/>成功レスポンス]
    Operation -->|DB エラー| DatabaseError[HTTP 500<br/>Database Error]
    
    ClientError --> ErrorResponse[エラーレスポンス]
    ServerError --> ErrorResponse
    NotFound --> ErrorResponse
    DatabaseError --> ErrorResponse
    Success --> SuccessResponse[成功レスポンス]
    
    ErrorResponse --> Frontend[フロントエンドでエラー表示]
    SuccessResponse --> Frontend2[フロントエンドでデータ表示]
```

## 開発環境起動フロー

```mermaid
flowchart TD
    Start[開発開始] --> LocalStack{LocalStack起動}
    
    LocalStack -->|make localstack-up| Docker[Docker Compose起動]
    Docker --> DynamoDB[DynamoDB準備完了]
    
    DynamoDB --> SAM{SAM Local起動}
    SAM -->|make backend-start| Lambda[Lambda Functions起動<br/>SAM Local Runtime]
    Lambda --> APIReady[API Gateway準備完了 :3001<br/>Lambda → LocalStack DynamoDB接続]
    
    APIReady --> Vite{Vite起動}
    Vite -->|make frontend-start| DevServer[Development Server起動]
    DevServer --> UIReady[UI準備完了 :3000]
    
    UIReady --> Ready[🚀 アプリケーション起動完了]
    
    Ready --> Test{テスト実行}
    Test -->|make test| Backend[Backend Tests]
    Test -->|make test| Frontend[Frontend Tests]
    
    Backend --> pytest[pytest実行]
    Frontend --> vitest[Vitest実行]
    
    pytest --> TestResults[テスト結果]
    vitest --> TestResults
    TestResults --> Development[開発継続]
```

## データフロー図

```mermaid
flowchart LR
    subgraph "Data Layer"
        DDB[(DynamoDB<br/>LocalStack)]
    end
    
    subgraph "Business Logic Layer"
        GetTodos[Get Todos<br/>Lambda]
        CreateTodo[Create Todo<br/>Lambda]
        UpdateTodo[Update Todo<br/>Lambda]
        DeleteTodo[Delete Todo<br/>Lambda]
    end
    
    subgraph "API Layer"
        Gateway[API Gateway<br/>SAM Local]
    end
    
    subgraph "Service Layer"
        TodoAPI[todoApi.js<br/>Axios Service]
    end
    
    subgraph "Presentation Layer"
        Vue[Vue.js Component<br/>App.vue]
        Quasar[Quasar UI<br/>Components]
    end
    
    Vue <--> Quasar
    Vue <--> TodoAPI
    TodoAPI <--> Gateway
    Gateway <--> GetTodos
    Gateway <--> CreateTodo
    Gateway <--> UpdateTodo
    Gateway <--> DeleteTodo
    GetTodos <--> DDB
    CreateTodo <--> DDB
    UpdateTodo <--> DDB
    DeleteTodo <--> DDB
```

## テスト実行フロー

```mermaid
flowchart TD
    TestStart[テスト開始] --> BackendTest{バックエンドテスト}
    BackendTest --> UnitTest[Unit Tests<br/>pytest]
    BackendTest --> IntegrationTest[Integration Tests<br/>pytest + moto]
    
    UnitTest --> Lambda1Test[Lambda Functions Test]
    UnitTest --> ValidationTest[Validation Test]
    UnitTest --> ErrorTest[Error Handling Test]
    
    IntegrationTest --> APITest[API Endpoints Test]
    IntegrationTest --> DynamoDBTest[DynamoDB Mock Test]
    
    TestStart --> FrontendTest{フロントエンドテスト}
    FrontendTest --> ComponentTest[Component Tests<br/>Vitest + Vue Test Utils]
    FrontendTest --> ServiceTest[Service Tests<br/>Vitest + Mock]
    
    ComponentTest --> VueTest[Vue Component Test]
    ComponentTest --> UITest[UI Interaction Test]
    
    ServiceTest --> APIServiceTest[API Service Test]
    ServiceTest --> MockTest[Mock Test]
    
    Lambda1Test --> Results[テスト結果]
    ValidationTest --> Results
    ErrorTest --> Results
    APITest --> Results
    DynamoDBTest --> Results
    VueTest --> Results
    UITest --> Results
    APIServiceTest --> Results
    MockTest --> Results
    
    Results --> Report[📊 テストレポート<br/>Coverage Report]
    Report --> PassFail{全テスト成功?}
    PassFail -->|成功| Deploy[🚀 デプロイ可能]
    PassFail -->|失敗| Debug[🔧 デバッグ必要]
```