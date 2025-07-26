// 簡素化された認証サービス（テスト用）
console.log('authService.js loading...')

class AuthService {
  constructor() {
    console.log('AuthService constructor called')
    this.currentUser = null
    this.isAuthenticated = false
    this.authListeners = []
  }

  // 認証状態変更リスナー
  addAuthListener(callback) {
    this.authListeners.push(callback)
  }

  removeAuthListener(callback) {
    this.authListeners = this.authListeners.filter(listener => listener !== callback)
  }

  notifyAuthChange() {
    this.authListeners.forEach(callback => callback(this.isAuthenticated, this.currentUser))
  }

  // 簡易ログイン（テスト用）
  async signIn(email, password) {
    console.log('signIn called with:', email)
    
    // 簡易実装
    setTimeout(() => {
      const mockUser = {
        username: email,
        email: email,
        name: 'Test User'
      }
      
      this.currentUser = mockUser
      this.isAuthenticated = true
      this.notifyAuthChange()
      
      return { user: mockUser }
    }, 500)
  }

  // ログアウト
  async signOut() {
    console.log('signOut called')
    this.currentUser = null
    this.isAuthenticated = false
    this.notifyAuthChange()
    return true
  }

  // 現在の認証状態を確認
  async getCurrentSession() {
    console.log('getCurrentSession called')
    return this.isAuthenticated ? { user: this.currentUser } : null
  }

  // アクセストークンを取得
  async getAccessToken() {
    console.log('getAccessToken called')
    return this.isAuthenticated ? 'mock-token' : null
  }

  // 初期化時に認証状態を復元
  async initializeAuth() {
    console.log('initializeAuth called')
    return false
  }
}

// シングルトンインスタンス
console.log('Creating AuthService instance...')
const authService = new AuthService()
console.log('AuthService instance created:', authService)

export default authService