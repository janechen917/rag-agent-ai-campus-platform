import { createI18n } from 'vue-i18n'
import zhCn from './locales/zh-cn'
import zhTw from './locales/zh-tw'
import en from './locales/en'

const savedLocale = localStorage.getItem('locale') || 'zh-cn'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'zh-cn',
  messages: {
    'zh-cn': zhCn,
    'zh-tw': zhTw,
    'en': en
  }
})

export default i18n
