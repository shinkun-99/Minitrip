import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './TripForm.css';

const TripForm = ({ onSubmit, isLoading }) => {
  const { t } = useTranslation();
  const today = new Date().toISOString().split('T')[0];

  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    start_date: today,
    end_date: new Date(new Date().setDate(new Date().getDate() + 2)).toISOString().split('T')[0],
    interests: [],
    pace: 'relaxed',
    other_requirements: '',
  });

  const availableInterests = ['history', 'food', 'nature', 'art', 'adventure', 'shopping', 'nightlife', 'relaxation'];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleInterestChange = (e) => {
    const { value, checked } = e.target;
    setFormData((prev) => {
      const newInterests = checked
        ? [...prev.interests, value]
        : prev.interests.filter((interest) => interest !== value);
      return { ...prev, interests: newInterests };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.destination || !formData.start_date || !formData.end_date) {
        alert(t('form.alert.fillDestinationDates'));
        return;
    }
    if (new Date(formData.start_date) > new Date(formData.end_date)) {
        alert(t('form.alert.endDateAfterStartDate'));
        return;
    }
    const startDate = new Date(formData.start_date);
    const endDate = new Date(formData.end_date);
    const diffTime = Math.abs(endDate - startDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    const submissionData = {
        ...formData,
        days: diffDays 
    };
    onSubmit(submissionData);
  };

  return (
    <form onSubmit={handleSubmit} className="trip-form">
      
      <div className="form-group">
        <label htmlFor="origin">{t('form.label.origin')}</label>
        <input
          type="text"
          id="origin"
          name="origin"
          value={formData.origin}
          onChange={handleChange}
          placeholder={t('form.placeholder.origin')}
        />
      </div>

      <div className="form-group">
        <label htmlFor="destination">{t('form.label.destination')}</label>
        <input
          type="text"
          id="destination"
          name="destination"
          value={formData.destination}
          onChange={handleChange}
          placeholder={t('form.placeholder.destination')}
          required
        />
      </div>

      <div className="form-group-inline">
        <div className="form-group">
            <label htmlFor="start_date">{t('form.label.startDate')}</label>
            <input
            type="date"
            id="start_date"
            name="start_date"
            value={formData.start_date}
            min={today}
            onChange={handleChange}
            required
            />
        </div>
        <div className="form-group">
            <label htmlFor="end_date">{t('form.label.endDate')}</label>
            <input
            type="date"
            id="end_date"
            name="end_date"
            value={formData.end_date}
            min={formData.start_date || today}
            onChange={handleChange}
            required
            />
        </div>
      </div>

      <div className="form-group">
        <label>{t('form.label.interests')}</label>
        <div className="interests-group">
          {availableInterests.map((interest) => (
            <label key={interest} className="interest-label">
              <input
                type="checkbox"
                name="interests"
                value={interest}
                checked={formData.interests.includes(interest)}
                onChange={handleInterestChange}
              /> {t(`form.interest.${interest}`)}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>{t('form.label.pace')}</label>
        <div className="pace-group">
          <label>
            <input type="radio" name="pace" value="relaxed" checked={formData.pace === 'relaxed'} onChange={handleChange}/> {t('form.pace.relaxed')}
          </label>
          <label>
            <input type="radio" name="pace" value="moderate" checked={formData.pace === 'moderate'} onChange={handleChange}/> {t('form.pace.moderate')}
          </label>
          <label>
            <input type="radio" name="pace" value="packed" checked={formData.pace === 'packed'} onChange={handleChange}/> {t('form.pace.packed')}
          </label>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="other_requirements">{t('form.label.otherRequirements')}</label>
        <textarea
          id="other_requirements"
          name="other_requirements"
          value={formData.other_requirements}
          onChange={handleChange}
          rows="5"
          placeholder={t('form.placeholder.otherRequirements')}
        />
      </div>
      
      <button type="submit" disabled={isLoading} className="submit-button">
        {isLoading ? t('form.button.submitting') : t('form.button.submit')}
      </button>
    </form>
  );
};

export default TripForm;