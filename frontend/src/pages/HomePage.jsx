import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import TripForm from '../components/TripForm';
import ItineraryDisplay from '../components/ItineraryDisplay';
import LoadingSpinner from '../components/LoadingSpinner';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { planTrip, getHealth } from '../services/api';
import './HomePage.css';

const HomePage = () => {
  const { t, i18n } = useTranslation();
  const [itinerary, setItinerary] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState(t('home.backendStatus.checking'));

  // 当语言改变时，更新初始的 backendStatus 文本
  useEffect(() => {
    setBackendStatus(t('home.backendStatus.checking'));

    const checkBackend = async () => {
        try {
            const health = await getHealth();
            setBackendStatus(t('home.backendStatus.reachable', { message: health.message, status: health.status }));
        } catch (err) {
            setBackendStatus(t('home.backendStatus.notReachable'));
            setError(t('home.error.couldNotConnect'));
        }
    };
    checkBackend();
  }, [t, i18n.language]);


  const handleFormSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    setItinerary(null);

    const currentLang = i18n.language.split('-')[0];
    const submissionData = {
      ...formData,
      target_language: currentLang

  };

    console.log("DEBUG [HomePage]: Submitting data to backend:", submissionData); 

    try {
      const result = await planTrip(submissionData);
      if (result.error) {
        setError(result.error);
      } else {
        setItinerary(result);
      }
    } catch (err) {
      console.error("Full error object caught in HomePage:", err);
      if (err && err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else if (err && err.error) {
        setError(err.error);
      } else if (err && err.message) {
        setError(err.message);
      } else {
        setError(t('home.error.unexpected'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home-page">
       <div style={{ position: 'absolute', top: '10px', right: '10px', zIndex: 10 }}>
        <LanguageSwitcher />
      </div>
      <header className="app-header">
        <h1>{t('home.title')}</h1>
        <p className="backend-status">{backendStatus}</p>
      </header>
      <main>
        <TripForm onSubmit={handleFormSubmit} isLoading={isLoading} />
        {isLoading && <LoadingSpinner message={t('itinerary.loadingMessage')} />}
        {error && <div className="error-message">Error: {error}</div>}
        {itinerary && !isLoading && <ItineraryDisplay itineraryData={itinerary} />}
      </main>
      <footer className="app-footer">
        <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
      </footer>
    </div>
  );
};

export default HomePage;