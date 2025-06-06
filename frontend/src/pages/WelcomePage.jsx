import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../components/LanguageSwitcher';
import './WelcomePage.css';

const WelcomePage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleStartPlanning = () => {
    navigate('/home');
  };

  return (
    <div className="welcome-container">
      <div style={{ position: 'absolute', top: '20px', right: '20px' }}>
        <LanguageSwitcher />
      </div>
      <h1 className="welcome-title gradient-text">
        {t('welcome.titleLine1')}
        <br />
        {t('welcome.titleLine2')}
      </h1>
      <button className="welcome-button" onClick={handleStartPlanning}>
        {t('welcome.getStartedButton')}
      </button>
    </div>
  );
};

export default WelcomePage;