import React, { useState, useEffect } from 'react';
import QRDisplay from './components/QRDisplay';
import Login from './components/Login';
import {
  getDeviceId, setDeviceId, DEVICE_IDS,
  connectWebSocket, saveCurrentQR, getCurrentQR, fetchActiveOrder,
  getLocationId, setLocationId, getLocationName, setLocationName, fetchLocations,
  login, logout, isAuthenticated, getCurrentUser, getMe
} from './api';
import './App.css';

function App() {
  // Auth state
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [user, setUser] = useState(getCurrentUser());
  const [loginError, setLoginError] = useState(null);

  // App state
  const [deviceId, setDeviceIdState] = useState('');
  const [locationId, setLocationIdState] = useState('');
  const [locationName, setLocationNameState] = useState('');
  const [qrData, setQrData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [showSetup, setShowSetup] = useState(false);
  const [setupStep, setSetupStep] = useState('location'); // 'location' or 'device'
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);

  // Check auth on mount
  useEffect(() => {
    if (authenticated) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await getMe();
      setUser(userData);
      init(userData);
    } catch (error) {
      console.error('Auth check failed:', error);
      handleLogout();
      setLoading(false);
    }
  };

  const init = async (userData) => {
    const savedLocationId = getLocationId();
    const savedLocationName = getLocationName();
    const savedDeviceId = getDeviceId();

    if (savedLocationId && savedDeviceId) {
      // Verify user still has access to this location
      const locs = await fetchLocations();
      setLocations(locs);

      const hasAccess = locs.some(loc => loc.id === savedLocationId);
      if (hasAccess) {
        setLocationIdState(savedLocationId);
        setLocationNameState(savedLocationName || '');
        setDeviceIdState(savedDeviceId);
        // Восстанавливаем QR из localStorage
        const savedQR = getCurrentQR();
        if (savedQR) {
          setQrData(savedQR);
        }
      } else {
        // No access anymore, reset
        setShowSetup(true);
        setSetupStep('location');
      }
    } else {
      // Load locations for setup
      const locs = await fetchLocations();
      setLocations(locs);
      setShowSetup(true);
      setSetupStep(savedLocationId ? 'device' : 'location');
      if (savedLocationId) {
        setLocationIdState(savedLocationId);
        setLocationNameState(savedLocationName || '');
      }
    }
    setLoading(false);
  };

  // При подключении проверяем активный заказ на сервере
  useEffect(() => {
    if (!deviceId || !locationId || !connected) return;

    const checkActiveOrder = async () => {
      const order = await fetchActiveOrder(deviceId, locationId);
      if (order) {
        const qr = {
          url: `${window.location.origin.replace('display', 'track')}/?t=${order.token}`,
          humanId: order.human_id,
        };
        setQrData(qr);
        saveCurrentQR(qr);
      }
    };

    checkActiveOrder();
  }, [deviceId, locationId, connected]);

  useEffect(() => {
    if (!deviceId || !locationId) return;

    const ws = connectWebSocket(deviceId, handleWebSocketMessage, locationId);

    ws.addEventListener('open', () => setConnected(true));
    ws.addEventListener('close', () => setConnected(false));

    return () => ws.close();
  }, [deviceId, locationId]);

  const handleWebSocketMessage = (message) => {
    console.log('WebSocket message:', message);

    if (message.type === 'SHOW_QR') {
      const qr = {
        url: message.url,
        humanId: message.human_id,
      };
      setQrData(qr);
      saveCurrentQR(qr);
    } else if (message.type === 'ORDER_SCANNED' || message.type === 'CLEAR_QR') {
      // QR отсканирован - убираем
      setQrData(null);
      saveCurrentQR(null);
    }
  };

  // Login handlers
  const handleLogin = async (username, password) => {
    setLoginError(null);
    try {
      const data = await login(username, password);
      setUser(data.user);
      setAuthenticated(true);
      setLoading(true);
      init(data.user);
    } catch (error) {
      setLoginError(error.message || 'Ошибка входа');
    }
  };

  const handleLogout = () => {
    logout();
    setAuthenticated(false);
    setUser(null);
    setDeviceIdState('');
    setLocationIdState('');
    setLocationNameState('');
    setQrData(null);
    setLocations([]);
    setShowSetup(false);
  };

  const handleSelectLocation = (loc) => {
    setLocationId(loc.id);
    setLocationIdState(loc.id);
    setLocationName(loc.name + (loc.mall_name ? ` (${loc.mall_name})` : ''));
    setLocationNameState(loc.name + (loc.mall_name ? ` (${loc.mall_name})` : ''));
    setSetupStep('device');
  };

  const handleSelectDevice = (id) => {
    setDeviceId(id);
    setDeviceIdState(id);
    setShowSetup(false);
    // Очищаем старый QR при смене устройства
    saveCurrentQR(null);
  };

  const handleChangeDevice = async () => {
    const locs = await fetchLocations();
    setLocations(locs);
    setShowSetup(true);
    setSetupStep('location');
    setQrData(null);
    saveCurrentQR(null);
  };

  // Show login if not authenticated
  if (!authenticated) {
    return <Login onLogin={handleLogin} error={loginError} />;
  }

  if (loading) {
    return <div className="app"><div className="loading">Загрузка...</div></div>;
  }

  // Экран выбора локации
  if (showSetup && setupStep === 'location') {
    // Group locations by organization
    const grouped = locations.reduce((acc, loc) => {
      if (!acc[loc.organization_name]) {
        acc[loc.organization_name] = [];
      }
      acc[loc.organization_name].push(loc);
      return acc;
    }, {});

    return (
      <div className="app">
        <div className="setup-screen">
          <div className="setup-content">
            <div className="logo">📺</div>
            <h1>QR Queue Display</h1>
            <p className="user-badge">👤 {user?.full_name || user?.username}</p>
            <p>Выберите точку</p>

            <div className="location-list">
              {Object.entries(grouped).map(([orgName, locs]) => (
                <div key={orgName} className="location-group">
                  <h3 className="org-name">{orgName}</h3>
                  {locs.map((loc) => (
                    <button
                      key={loc.id}
                      className="location-button"
                      onClick={() => handleSelectLocation(loc)}
                    >
                      <span className="loc-name">{loc.name}</span>
                      {loc.mall_name && <span className="loc-mall">{loc.mall_name}</span>}
                      {loc.city && <span className="loc-city">{loc.city}</span>}
                    </button>
                  ))}
                </div>
              ))}
            </div>

            <button className="logout-btn" onClick={handleLogout}>
              🚪 Выйти
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Экран выбора планшета
  if (showSetup && setupStep === 'device') {
    return (
      <div className="app">
        <div className="setup-screen">
          <div className="setup-content">
            <div className="logo">📺</div>
            <h1>QR Queue Display</h1>
            <p className="selected-location">
              📍 {locationName}
            </p>
            <p>Выберите номер планшета</p>

            <div className="device-buttons">
              {DEVICE_IDS.map((device) => (
                <button
                  key={device.id}
                  className="device-button"
                  onClick={() => handleSelectDevice(device.id)}
                >
                  {device.name}
                </button>
              ))}
            </div>

            <button
              className="back-button"
              onClick={() => setSetupStep('location')}
            >
              ← Выбрать другую точку
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentDevice = DEVICE_IDS.find(d => d.id === deviceId);

  return (
    <div className="app">
      {qrData ? (
        <QRDisplay
          url={qrData.url}
          humanId={qrData.humanId}
        />
      ) : (
        <div className="idle-screen">
          <div className="idle-content">
            <div className="logo">📺</div>
            <h1>QR Queue Display</h1>
            <p>Ожидание заказа...</p>

            <div className="device-info">
              <div className={`status-dot ${connected ? 'connected' : 'disconnected'}`} />
              <span>{connected ? 'Подключено' : 'Нет соединения'}</span>
            </div>

            <div className="location-info">
              📍 {locationName}
            </div>

            <div className="device-id">
              <strong>{currentDevice?.name || deviceId}</strong>
              <button className="change-device-btn" onClick={handleChangeDevice}>
                Настройки
              </button>
            </div>

            <button className="logout-btn-small" onClick={handleLogout}>
              Выйти
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
