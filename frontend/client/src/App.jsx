import React, { useState, useEffect } from 'react';
import OrderStatus from './components/OrderStatus';
import {
  getTokenFromUrl,
  getOrderByToken,
  connectWebSocket,
  vibrate,
  requestNotificationPermission,
  showNotification,
} from './api';
import './App.css';

function App() {
  const [token, setToken] = useState(null);
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [previousStatus, setPreviousStatus] = useState(null);

  useEffect(() => {
    const urlToken = getTokenFromUrl();
    
    if (!urlToken) {
      setError('Неверная ссылка. QR-код не содержит токен.');
      setLoading(false);
      return;
    }
    
    setToken(urlToken);
    requestNotificationPermission();
  }, []);

  useEffect(() => {
    if (!token) return;

    // Load initial order data
    loadOrder(token);

    // Connect WebSocket for real-time updates
    const ws = connectWebSocket(token, handleWebSocketMessage);

    return () => ws.close();
  }, [token]);

  const loadOrder = async (token) => {
    try {
      const data = await getOrderByToken(token);
      setOrder(data);
      setPreviousStatus(data.status);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load order:', err);
      setError('Заказ не найден');
      setLoading(false);
    }
  };

  const handleWebSocketMessage = (message) => {
    console.log('WebSocket message:', message);
    
    if (message.type === 'STATUS_UPDATE') {
      setOrder((prev) => ({
        ...prev,
        status: message.status,
      }));
      
      // Notify user of status change
      if (message.status === 'ready') {
        vibrate([200, 100, 200, 100, 200]);
        showNotification('Заказ готов!', `Заказ ${message.human_id} готов к выдаче`);
      } else {
        vibrate([100]);
      }
      
      setPreviousStatus(message.status);
    }
  };

  if (loading) {
    return (
      <div className="app loading">
        <div className="spinner" />
        <p>Загрузка...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app error">
        <div className="error-icon">❌</div>
        <h2>Ошибка</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className={`app ${order?.status === 'ready' ? 'ready' : ''}`}>
      <div className="app-header">
        <h1>🎯 QR Queue</h1>
        <p>Отслеживание заказа</p>
      </div>

      <div className="app-content">
        {order && (
          <OrderStatus status={order.status} humanId={order.human_id} />
        )}
      </div>

      <div className="app-footer">
        <p>Не закрывайте эту страницу</p>
        <p>Мы уведомим вас, когда заказ будет готов</p>
      </div>
    </div>
  );
}

export default App;
