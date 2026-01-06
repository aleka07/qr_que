import React, { useState, useRef } from 'react';
import './NumPad.css';

const NumPad = ({ value, onChange, onSubmit, deviceId, onDeviceChange, loading }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submitTimeoutRef = useRef(null);

  const handleNumberClick = (num) => {
    onChange(value + num);
  };

  const handleClear = () => {
    onChange('');
  };

  const handleBackspace = () => {
    onChange(value.slice(0, -1));
  };

  const handleSubmit = async () => {
    if (value.trim() && deviceId && !isSubmitting && !loading) {
      // Prevent double-clicks with local state
      setIsSubmitting(true);

      // Clear any pending timeout
      if (submitTimeoutRef.current) {
        clearTimeout(submitTimeoutRef.current);
      }

      try {
        await onSubmit();
      } finally {
        // Reset after a short delay to prevent rapid re-clicks
        submitTimeoutRef.current = setTimeout(() => {
          setIsSubmitting(false);
        }, 500);
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && value.trim() && deviceId && !isSubmitting && !loading) {
      handleSubmit();
    } else if (e.key === 'Backspace') {
      handleBackspace();
    } else if (/^[0-9]$/.test(e.key)) {
      handleNumberClick(e.key);
    }
  };

  React.useEffect(() => {
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [value, deviceId, isSubmitting, loading]);

  const isDisabled = !value.trim() || !deviceId || isSubmitting || loading;

  return (
    <div className="numpad-container">
      <div className="numpad-header">
        <h2>Создать заказ</h2>
      </div>

      <div className="device-selector">
        <label>Планшет:</label>
        <select value={deviceId} onChange={(e) => onDeviceChange(e.target.value)}>
          <option value="">Выберите планшет</option>
          <option value="tab_1">Планшет 1</option>
          <option value="tab_2">Планшет 2</option>
          <option value="tab_3">Планшет 3</option>
        </select>
      </div>

      <div className="numpad-display">
        <input
          type="text"
          value={value}
          placeholder="Введите номер заказа"
          readOnly
        />
      </div>

      <div className="numpad-grid">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
          <button
            key={num}
            className="numpad-button"
            onClick={() => handleNumberClick(num.toString())}
            disabled={isSubmitting || loading}
          >
            {num}
          </button>
        ))}

        <button className="numpad-button" onClick={handleClear} disabled={isSubmitting || loading}>
          C
        </button>

        <button className="numpad-button" onClick={() => handleNumberClick('0')} disabled={isSubmitting || loading}>
          0
        </button>

        <button className="numpad-button" onClick={handleBackspace} disabled={isSubmitting || loading}>
          ←
        </button>
      </div>

      <button
        className={`numpad-submit ${isSubmitting || loading ? 'submitting' : ''}`}
        onClick={handleSubmit}
        disabled={isDisabled}
      >
        {isSubmitting || loading ? 'Создание...' : 'Создать заказ (Enter)'}
      </button>
    </div>
  );
};

export default NumPad;
