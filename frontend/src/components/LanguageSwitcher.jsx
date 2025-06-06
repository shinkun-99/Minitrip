import React from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageSwitcher.css';

const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  const currentLanguage = i18n.resolvedLanguage || i18n.language.split('-')[0] || 'en';


  return (
    <div className="language-switcher">
      <button 
        onClick={() => changeLanguage('en')} 
        disabled={currentLanguage === 'en'}
        className={currentLanguage === 'en' ? 'active' : ''}
      >
        {t('languageSwitcher.english')}
      </button>
      <button 
        onClick={() => changeLanguage('zh')} 
        disabled={currentLanguage === 'zh'}
        className={currentLanguage === 'zh' ? 'active' : ''}
      >
        {t('languageSwitcher.chinese')}
      </button>
      <button 
        onClick={() => changeLanguage('ja')} 
        disabled={currentLanguage === 'ja'}
        className={currentLanguage === 'ja' ? 'active' : ''}
      >
        {t('languageSwitcher.japanese')}
      </button>
    </div>
  );
};

export default LanguageSwitcher;