// Todo型定義（JavaScriptでのJSDoc形式）

/**
 * @typedef {Object} Todo
 * @property {string} user_id - ユーザーID
 * @property {string} todo_id - TodoのID
 * @property {string} title - Todoのタイトル
 * @property {string} description - Todoの説明
 * @property {boolean} completed - 完了状態
 * @property {string} priority - 優先度 ('low' | 'medium' | 'high')
 * @property {string} created_at - 作成日時
 * @property {string} updated_at - 更新日時
 */

/**
 * @typedef {Object} CreateTodoRequest
 * @property {string} user_id - ユーザーID
 * @property {string} title - Todoのタイトル
 * @property {string} [description] - Todoの説明（オプション）
 * @property {string} [priority] - 優先度（オプション）
 */

/**
 * @typedef {Object} UpdateTodoRequest
 * @property {string} user_id - ユーザーID
 * @property {string} [title] - Todoのタイトル（オプション）
 * @property {string} [description] - Todoの説明（オプション）
 * @property {boolean} [completed] - 完了状態（オプション）
 * @property {string} [priority] - 優先度（オプション）
 */

/**
 * @typedef {Object} TodosResponse
 * @property {Todo[]} todos - Todoの配列
 * @property {number} count - Todoの総数
 */

export default {}