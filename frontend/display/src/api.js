const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Предустановленные ID планшетов (должны совпадать со Staff App)
export const DEVICE_IDS = [
  { id: 'tab_1', name: 'Планшет 1' },
  { id: 'tab_2', name: 'Планшет 2' },
  { id: 'tab_3', name: 'Планшет 3' },
  { id: 'tab_4', name: 'Планшет 4' },
];

export const getDeviceId = () => {
  return localStorage.getItem('device_id') || null;
};

export const setDeviceId = (deviceId) => {
  localStorage.setItem('device_id', deviceId);
};

// Сохранение текущего QR кода
export const saveCurrentQR = (qrData) => {
  if (qrData) {
    localStorage.setItem('current_qr', JSON.stringify(qrData));
  } else {
    localStorage.removeItem('current_qr');
  }
};

export const getCurrentQR = () => {
  const data = localStorage.getItem('current_qr');
  return data ? JSON.parse(data) : null;
};

// Получение активного заказа для устройства
export const fetchActiveOrder = async (deviceId) => {
  try {
    const response = await fetch(`${API_URL}/orders/active?device_id=${deviceId}`);
    if (response.ok) {
      const orders = await response.json();
      // Находим заказ со статусом pending (ещё не отсканирован)
      const pendingOrder = orders.find(o => o.status === 'pending');
      return pendingOrder || null;
    }
    return null;
  } catch (error) {
    console.error('Error fetching active order:', error);
    return null;
  }
};

export const connectWebSocket = (deviceId, onMessage) => {
  const ws = new WebSocket(`${WS_URL}/ws/display/${deviceId}`);
  
  ws.onopen = () => {
    console.log('Display WebSocket connected:', deviceId);
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...');
    setTimeout(() => connectWebSocket(deviceId, onMessage), 3000);
  };
  
  return ws;
};
