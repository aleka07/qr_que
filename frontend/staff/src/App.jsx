import React, { useState, useEffect } from 'react';
import NumPad from './components/NumPad';
import OrderList from './components/OrderList';
import Login from './components/Login';
import { 
  createOrder, 
  getActiveOrders, 
  updateOrderStatus, 
  connectWebSocket,
  login,
  logout,
  isAuthenticated,
  getCurrentUser,
  getMe,
  getLocations
} from './api';
import './App.css';

function App() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [user, setUser] = useState(getCurrentUser());
  const [loginError, setLoginError] = useState(null);
  
  const [orders, setOrders] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [deviceId, setDeviceId] = useState('tab_1');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);
  
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);

  // Check auth on mount
  useEffect(() => {
    if (authenticated) {
      checkAuth();
    }
  }, []);

  // Load locations when authenticated
  useEffect(() => {
    if (authenticated && user) {
      loadLocations();
    }
  }, [authenticated, user]);

  // Load orders when location is selected
  useEffect(() => {
    if (authenticated && (selectedLocation || user?.role === 'admin')) {
      loadOrders();
    }
  }, [authenticated, selectedLocation, user]);

  // Connect WebSocket
  useEffect(() => {
    if (!authenticated) return;
    
    const locationId = selectedLocation?.id || (user?.location_id);
    const ws = connectWebSocket(handleWebSocketMessage, locationId);
    return () => ws.close();
  }, [authenticated, selectedLocation, user]);

  const checkAuth = async () => {
    try {
      const userData = await getMe();
      setUser(userData);
      
      // If user has a specific location, select it
      if (userData.location_id) {
        setSelectedLocation({ id: userData.location_id });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      handleLogout();
    }
  };

  const loadLocations = async () => {
    try {
      const data = await getLocations();
      setLocations(data);
      
      // Auto-select first location if user doesn't have one assigned
      if (!user.location_id && data.length > 0 && !selectedLocation) {
        setSelectedLocation(data[0]);
      } else if (user.location_id) {
        const userLocation = data.find(l => l.id === user.location_id);
        if (userLocation) {
          setSelectedLocation(userLocation);
        }
      }
    } catch (error) {
      console.error('Failed to load locations:', error);
    }
  };

  const loadOrders = async () => {
    try {
      const locationId = selectedLocation?.id || user?.location_id;
      const data = await getActiveOrders(locationId);
      setOrders(data);
    } catch (error) {
      console.error('Failed to load orders:', error);
      showNotification('Ошибка загрузки заказов', 'error');
    }
  };

  const handleLogin = async (username, password) => {
    setLoginError(null);
    try {
      const data = await login(username, password);
      setUser(data.user);
      setAuthenticated(true);
      
      if (data.user.location_id) {
        setSelectedLocation({ id: data.user.location_id });
      }
    } catch (error) {
      setLoginError(error.message || 'Ошибка входа');
    }
  };

  const handleLogout = () => {
    logout();
    setAuthenticated(false);
    setUser(null);
    setOrders([]);
    setSelectedLocation(null);
    setLocations([]);
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
      const locationId = selectedLocation?.id || user?.location_id;
      await createOrder(inputValue.trim(), deviceId, locationId);
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

  // Show login if not authenticated
  if (!authenticated) {
    return <Login onLogin={handleLogin} error={loginError} />;
  }

  const canChangeLocation = user?.role === 'admin' || user?.role === 'owner';

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>🎯 Staff Dashboard</h1>
          {selectedLocation && (
            <span className="location-badge">
              📍 {selectedLocation.name || 'Loading...'}
            </span>
          )}
        </div>
        <div className="header-right">
          {canChangeLocation && locations.length > 1 && (
            <select 
              className="location-select"
              value={selectedLocation?.id || ''}
              onChange={(e) => {
                const loc = locations.find(l => l.id === e.target.value);
                setSelectedLocation(loc);
              }}
            >
              {user?.role === 'admin' && (
                <option value="">Все точки</option>
              )}
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.name}
                </option>
              ))}
            </select>
          )}
          <div className="user-info">
            <span className="user-name">{user?.full_name || user?.username}</span>
            <span className="user-role">{user?.role}</span>
          </div>
          <button className="logout-button" onClick={handleLogout}>
            Выйти
          </button>
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
