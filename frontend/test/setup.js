import { config } from '@vue/test-utils'
import { Quasar } from 'quasar'

// Quasar をグローバルに設定
config.global.plugins = [Quasar]

// グローバルなmockを設定
global.ResizeObserver = class ResizeObserver {
  constructor(cb) {
    this.cb = cb
  }
  observe() {}
  unobserve() {}
  disconnect() {}
}

// console.error を抑制（テスト実行中の不要な警告を減らす）
const originalConsoleError = console.error
console.error = (...args) => {
  if (args[0]?.includes?.('Vue warn')) {
    return
  }
  originalConsoleError(...args)
}