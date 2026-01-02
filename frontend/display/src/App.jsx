import React, { useState, useEffect } from 'react';
import QRDisplay from './components/QRDisplay';
import { getDeviceId, setDeviceId, DEVICE_IDS, connectWebSocket, saveCurrentQR, getCurrentQR, fetchActiveOrder } from './api';
import './App.css';

function App() {
  const [deviceId, setDeviceIdState] = useState('');
  const [qrData, setQrData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [showSetup, setShowSetup] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = getDeviceId();
    if (id) {
      setDeviceIdState(id);
      // Восстанавливаем QR из localStorage
      const savedQR = getCurrentQR();
      if (savedQR) {
        setQrData(savedQR);
      }
    } else {
      setShowSetup(true);
    }
    setLoading(false);
  }, []);

  // При подключении проверяем активный заказ на сервере
  useEffect(() => {
    if (!deviceId || !connected) return;

    const checkActiveOrder = async () => {
      const order = await fetchActiveOrder(deviceId);
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
  }, [deviceId, connected]);

  useEffect(() => {
    if (!deviceId) return;

    const ws = connectWebSocket(deviceId, handleWebSocketMessage);
    
    ws.addEventListener('open', () => setConnected(true));
    ws.addEventListener('close', () => setConnected(false));

    return () => ws.close();
  }, [deviceId]);

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

  // Убираем автоматический timeout - QR висит пока не отсканируют
  const handleQRScanned = () => {
    console.log('QR scanned, clearing display');
    setQrData(null);
    saveCurrentQR(null);
  };

  const handleSelectDevice = (id) => {
    setDeviceId(id);
    setDeviceIdState(id);
    setShowSetup(false);
    // Очищаем старый QR при смене устройства
    saveCurrentQR(null);
  };

  const handleChangeDevice = () => {
    setShowSetup(true);
    setQrData(null);
    saveCurrentQR(null);
  };

  if (loading) {
    return <div className="app"><div className="loading">Загрузка...</div></div>;
  }

  // Экран выбора планшета
  if (showSetup) {
    return (
      <div className="app">
        <div className="setup-screen">
          <div className="setup-content">
            <div className="logo">🎯</div>
            <h1>QR Queue Display</h1>
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
            <div className="logo">🎯</div>
            <h1>QR Queue Display</h1>
            <p>Ожидание заказа...</p>
            
            <div className="device-info">
              <div className={`status-dot ${connected ? 'connected' : 'disconnected'}`} />
              <span>{connected ? 'Подключено' : 'Нет соединения'}</span>
            </div>
            
            <div className="device-id">
              <strong>{currentDevice?.name || deviceId}</strong>
              <button className="change-device-btn" onClick={handleChangeDevice}>
                Сменить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
