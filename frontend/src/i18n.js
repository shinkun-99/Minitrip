// 翻译文件
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpApi from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(HttpApi)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    supportedLngs: ['en', 'zh', 'ja'],
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    
    ns: ['translation'],
    defaultNS: 'translation',

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag', 'path', 'subdomain'],
      caches: ['localStorage'],
    },

    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json', 
    },

    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;