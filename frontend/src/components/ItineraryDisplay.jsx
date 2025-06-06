import React from 'react';
import { useTranslation } from 'react-i18next';
import './ItineraryDisplay.css';

const ItineraryDisplay = ({ itineraryData }) => {
  const { t } = useTranslation();

  if (!itineraryData) {
    return null;
  }

  const { 
    trip_title, 
    travel_dates_display,
    destination_local_time_display,
    destination_weather_summary,
    daily_plans, 
    travel_tips,
    recommendation_summary 
  } = itineraryData;

  return (
    <div className="itinerary-display">
      {trip_title && <h2>{trip_title}</h2>}
      
      {travel_dates_display && <p className="travel-dates"><strong>{t('itinerary.travelDatesLabel')}</strong> {travel_dates_display}</p>}
      {destination_local_time_display && destination_local_time_display !== "N/A" && (
        <p className="local-time"><strong>{t('itinerary.destinationTimeLabel')}</strong> {destination_local_time_display}</p>
      )}

      {destination_weather_summary && (
        <div className="weather-summary card">
          <h3>{t('itinerary.weatherOutlookLabel')}</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{destination_weather_summary}</p>
        </div>
      )}

      {daily_plans && daily_plans.length > 0 && (
        <div className="daily-plans">
          <h3>{t('itinerary.dailyPlansLabel')}</h3>
          {daily_plans.map((plan) => (
            <div key={plan.day} className="day-plan card">
              <h4>{t('itinerary.dayLabel', { day: plan.day })} ({plan.date || t('itinerary.dateNotAvailable')}): {plan.theme || t('itinerary.themeDefault')}</h4>
              
              {plan.daily_weather_forecast && plan.daily_weather_forecast !== "N/A" && (
                <p className="daily-weather-forecast">
                  <strong>{t('itinerary.dailyWeatherLabel')}</strong> {plan.daily_weather_forecast}
                </p>
              )}
              <ul>
                {plan.activities && plan.activities.map((activity, index) => (
                  <li key={index}>
                    <strong>{activity.time_slot}:</strong> {activity.activity}
                    {activity.reason && <em className="reason"> - {activity.reason}</em>}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {travel_tips && travel_tips.length > 0 && (
        <div className="travel-tips card">
          <h3>{t('itinerary.travelTipsLabel')}</h3>
          <ul>
            {travel_tips.map((tip, index) => (
              <li key={index}>{tip}</li>
            ))}
          </ul>
        </div>
      )}

      {recommendation_summary && (
         <div className="recommendation-summary card">
            <h3>{t('itinerary.recommendationSummaryLabel')}</h3>
            <p>{recommendation_summary}</p>
         </div>
      )}
    </div>
  );
};

export default ItineraryDisplay;