import { CognitoUserPool, CognitoUser, AuthenticationDetails, CognitoUserAttribute } from 'amazon-cognito-identity-js'

// Cognito設定（LocalStack環境では動的に設定）
const isLocalStack = process.env.NODE_ENV === 'development'

// LocalStack環境の場合のモック設定
const localStackConfig = {
  UserPoolId: 'us-east-1_123456789',
  ClientId: 'localstack-client-id'
}

// 本番環境の設定（実際の値は環境変数から取得）
const awsConfig = {
  UserPoolId: process.env.VITE_COGNITO_USER_POOL_ID || 'us-east-1_CHANGEME',
  ClientId: process.env.VITE_COGNITO_APP_CLIENT_ID || 'CHANGEME'
}

const poolData = isLocalStack ? localStackConfig : awsConfig
const userPool = new CognitoUserPool(poolData)

class AuthService {
  constructor() {
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

  // サインアップ
  async signUp(email, password, name) {
    return new Promise((resolve, reject) => {
      if (isLocalStack) {
        // LocalStack環境では簡易実装
        setTimeout(() => {
          resolve({
            user: { username: email },
            userConfirmed: true
          })
        }, 500)
        return
      }

      const attributeList = [
        new CognitoUserAttribute({
          Name: 'email',
          Value: email
        }),
        new CognitoUserAttribute({
          Name: 'name',
          Value: name
        })
      ]

      userPool.signUp(email, password, attributeList, null, (err, result) => {
        if (err) {
          reject(err)
          return
        }
        resolve(result)
      })
    })
  }

  // ログイン
  async signIn(email, password) {
    return new Promise((resolve, reject) => {
      if (isLocalStack) {
        // LocalStack環境では簡易実装
        setTimeout(() => {
          const mockUser = {
            username: email,
            attributes: {
              email: email,
              name: 'Test User',
              sub: 'test-user-id-123'
            }
          }
          const mockTokens = {
            accessToken: 'mock-access-token',
            idToken: 'mock-id-token',
            refreshToken: 'mock-refresh-token'
          }

          this.currentUser = mockUser
          this.isAuthenticated = true
          
          // トークンをローカルストレージに保存
          localStorage.setItem('cognitoTokens', JSON.stringify(mockTokens))
          localStorage.setItem('currentUser', JSON.stringify(mockUser))
          
          this.notifyAuthChange()
          resolve({ user: mockUser, tokens: mockTokens })
        }, 500)
        return
      }

      const userData = {
        Username: email,
        Pool: userPool
      }

      const cognitoUser = new CognitoUser(userData)
      const authenticationData = {
        Username: email,
        Password: password
      }
      const authenticationDetails = new AuthenticationDetails(authenticationData)

      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (session) => {
          this.currentUser = cognitoUser
          this.isAuthenticated = true

          const tokens = {
            accessToken: session.getAccessToken().getJwtToken(),
            idToken: session.getIdToken().getJwtToken(),
            refreshToken: session.getRefreshToken().getToken()
          }

          // トークンをローカルストレージに保存
          localStorage.setItem('cognitoTokens', JSON.stringify(tokens))
          
          this.notifyAuthChange()
          resolve({ user: cognitoUser, tokens, session })
        },
        onFailure: (err) => {
          reject(err)
        }
      })
    })
  }

  // ログアウト
  async signOut() {
    try {
      if (this.currentUser && !isLocalStack) {
        this.currentUser.signOut()
      }
      
      this.currentUser = null
      this.isAuthenticated = false
      
      // ローカルストレージからトークンを削除
      localStorage.removeItem('cognitoTokens')
      localStorage.removeItem('currentUser')
      
      this.notifyAuthChange()
      return true
    } catch (error) {
      console.error('Sign out error:', error)
      throw error
    }
  }

  // 現在の認証状態を確認
  async getCurrentSession() {
    try {
      if (isLocalStack) {
        // LocalStack環境では保存されたデータから復元
        const savedTokens = localStorage.getItem('cognitoTokens')
        const savedUser = localStorage.getItem('currentUser')
        
        if (savedTokens && savedUser) {
          this.currentUser = JSON.parse(savedUser)
          this.isAuthenticated = true
          return {
            user: this.currentUser,
            tokens: JSON.parse(savedTokens)
          }
        }
        return null
      }

      return new Promise((resolve, reject) => {
        const cognitoUser = userPool.getCurrentUser()
        if (!cognitoUser) {
          resolve(null)
          return
        }

        cognitoUser.getSession((err, session) => {
          if (err) {
            reject(err)
            return
          }

          if (!session.isValid()) {
            resolve(null)
            return
          }

          this.currentUser = cognitoUser
          this.isAuthenticated = true

          const tokens = {
            accessToken: session.getAccessToken().getJwtToken(),
            idToken: session.getIdToken().getJwtToken(),
            refreshToken: session.getRefreshToken().getToken()
          }

          resolve({ user: cognitoUser, tokens, session })
        })
      })
    } catch (error) {
      console.error('Get current session error:', error)
      return null
    }
  }

  // アクセストークンを取得
  async getAccessToken() {
    try {
      if (isLocalStack) {
        const savedTokens = localStorage.getItem('cognitoTokens')
        if (savedTokens) {
          const tokens = JSON.parse(savedTokens)
          return tokens.accessToken
        }
        return null
      }

      const session = await this.getCurrentSession()
      return session ? session.tokens.accessToken : null
    } catch (error) {
      console.error('Get access token error:', error)
      return null
    }
  }

  // ユーザー情報を取得
  async getUserInfo() {
    try {
      if (isLocalStack) {
        const savedUser = localStorage.getItem('currentUser')
        return savedUser ? JSON.parse(savedUser) : null
      }

      const session = await this.getCurrentSession()
      if (!session) return null

      return new Promise((resolve, reject) => {
        session.user.getUserAttributes((err, attributes) => {
          if (err) {
            reject(err)
            return
          }

          const userInfo = {}
          attributes.forEach(attr => {
            userInfo[attr.getName()] = attr.getValue()
          })

          resolve(userInfo)
        })
      })
    } catch (error) {
      console.error('Get user info error:', error)
      return null
    }
  }

  // 初期化時に認証状態を復元
  async initializeAuth() {
    try {
      const session = await this.getCurrentSession()
      if (session) {
        this.notifyAuthChange()
      }
      return session !== null
    } catch (error) {
      console.error('Initialize auth error:', error)
      return false
    }
  }
}

// シングルトンインスタンス
const authService = new AuthService()

export default authService
export { AuthService }