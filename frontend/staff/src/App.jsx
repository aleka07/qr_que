import React, { useState, useEffect } from 'react';
import NumPad from './components/NumPad';
import OrderList from './components/OrderList';
import { createOrder, getActiveOrders, updateOrderStatus, connectWebSocket } from './api';
import './App.css';

function App() {
  const [orders, setOrders] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [deviceId, setDeviceId] = useState('tab_1');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Load initial orders
  useEffect(() => {
    loadOrders();
  }, []);

  // Connect WebSocket
  useEffect(() => {
    const ws = connectWebSocket(handleWebSocketMessage);
    return () => ws.close();
  }, []);

  const loadOrders = async () => {
    try {
      const data = await getActiveOrders();
      setOrders(data);
    } catch (error) {
      console.error('Failed to load orders:', error);
      showNotification('Ошибка загрузки заказов', 'error');
    }
  };

  const handleWebSocketMessage = (message) => {
    console.log('WebSocket message:', message);
    
    if (message.type === 'NEW_ORDER') {
      setOrders((prev) => [message.order, ...prev]);
      showNotification(`Новый заказ: ${message.order.human_id}`, 'success');
    } else if (message.type === 'STATUS_UPDATE') {
      setOrders((prev) =>
        prev.map((order) =>
          order.id === message.order.id ? message.order : order
        )
      );
    }
  };

  const handleSubmit = async () => {
    if (!inputValue.trim() || !deviceId || loading) return;

    setLoading(true);
    try {
      await createOrder(inputValue.trim(), deviceId);
      setInputValue('');
      showNotification(`Заказ ${inputValue} создан`, 'success');
    } catch (error) {
      console.error('Failed to create order:', error);
      showNotification('Ошибка создания заказа', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await updateOrderStatus(orderId, newStatus);
    } catch (error) {
      console.error('Failed to update status:', error);
      showNotification('Ошибка обновления статуса', 'error');
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 Staff Dashboard</h1>
        <div className="connection-status">
          <span className="status-indicator"></span>
          Подключено
        </div>
      </header>

      <main className="app-main">
        <aside className="app-sidebar">
          <NumPad
            value={inputValue}
            onChange={setInputValue}
            onSubmit={handleSubmit}
            deviceId={deviceId}
            onDeviceChange={setDeviceId}
          />
        </aside>

        <section className="app-content">
          <OrderList orders={orders} onStatusChange={handleStatusChange} />
        </section>
      </main>

      {notification && (
        <div className={`notification notification-${notification.type}`}>
          {notification.message}
        </div>
      )}
    </div>
  );
}

export default App;
